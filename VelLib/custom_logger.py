from __future__ import annotations
import logging
from typing import Any, Dict
import inspect
from pprint import pformat
import sys

class VelLogger(logging.Logger):
    """カスタムロガークラス。コンテキスト情報を含むログ記録機能を提供。

    使用例:
        logger = VelLogger(__name__)
        logger.error("エラーメッセージ")  # 通常のエラーログ
        try:
            # エラーが発生する可能性のあるコード
        except Exception as e:
            logger.error_with_exc(e, "追加の説明")  # 例外情報を含むエラーログ

        # ローカル変数を含むデバッグログ
        logger.debug("デバッグ情報", log_local_vars=True, depth=1)

    log_local_vars: ローカル変数をログに含める（デフォルトはFalse）
    depth: ネストされたオブジェクトを展開する最大の深さ（デフォルトは0）
    """

    def __init__(self, name: str, recursion_limit: int = 100, *args: Any, **kwargs: Any) -> None:
        """
        インスタンスを初期化。

        Args:
            name (str): ロガーの名前
            recursion_limit (int): 再帰の最大深度（デフォルトは100）
            *args: 追加の位置引数
            **kwargs: 追加のキーワード引数
        """
        self.debug_relevant_attributes = ['__dict__', '__class__', '__name__', '__module__']
        super().__init__(name, *args, **kwargs)
        sys.setrecursionlimit(recursion_limit)

    def _get_extra(self, stack_level: int = 0) -> Dict[str, Any]:
        """
        現在のスタックフレームからコンテキスト情報を取得。

        Args:
            stack_level (int): 取得するスタックフレームのレベル

        Returns:
            Dict[str, Any]: コンテキスト情報を含む辞書
        """
        stack_level = stack_level + 1
        frame = inspect.stack()[stack_level]
        return {'_funcName': frame.function, '_fileName': frame.filename, '_lineno': frame.lineno}

    def _log_with_context(self, level: int, msg: str, stack_level: int = 1, *args: Any, **kwargs: Any) -> None:
        """
        コンテキスト情報を含むログを記録。

        Args:
            level (int): ログレベル
            msg (str): ログメッセージ
            stack_level (Optional[int]): スタックレベル（指定しない場合は3）
            *args: 追加の位置引数
            **kwargs: 追加のキーワード引数
        """
        stack_level = stack_level + 1
        log_local_vars = kwargs.pop('log_local_vars', False)
        max_depth = kwargs.pop('depth', 0)
        if log_local_vars:
            local_vars = f"\n{self._get_local_vars_str(stack_level, max_depth)}\n\n"
        else:
            local_vars = ""
        extra = kwargs.pop('extra', {})
        extra.update(self._get_extra(stack_level))
        super().log(level, f"{msg}\n{local_vars}", *args, extra=extra, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """CRITICALレベルのログを記録。"""
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """ERRORレベルのログを記録。"""
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """WARNINGレベルのログを記録。"""
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)

    def warn(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.warning(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """INFOレベルのログを記録。"""
        self._log_with_context(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """DEBUGレベルのログを記録。"""
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)

    def _log_with_exc(self, level: int, e: Exception, msg: str = "", *args: Any, **kwargs: Any) -> None:
        """
        例外情報を含むログを記録。

        Args:
            level (int): ログレベル
            e (Exception): ログに記録する例外オブジェクト
            msg (str): 追加のエラーメッセージ（デフォルトは空文字列）
        """
        stack_level = kwargs.pop('stack_level', 2)
        full_msg = f"{type(e).__name__}: {e}{f' {msg}' if msg else ''}"
        self._log_with_context(level, full_msg, exc_info=True, stack_level=stack_level, *args, **kwargs)

    def critical_with_exc(self, e: Exception, msg: str = "", *args: Any, **kwargs: Any) -> None:
        """
        例外情報を含む致命的なエラーログを記録。

        Args:
            e (Exception): ログに記録する例外オブジェクト
            msg (str, optional): 追加のエラーメッセージ。デフォルトは空文字列。
        """
        self._log_with_exc(logging.CRITICAL, e, msg, *args, **kwargs)

    def error_with_exc(self, e: Exception, msg: str = "", *args: Any, **kwargs: Any) -> None:
        """
        例外情報を含むエラーログを記録。

        Args:
            e (Exception): ログに記録する例外オブジェクト
            msg (str, optional): 追加のエラーメッセージ。デフォルトは空文字列。
        """
        self._log_with_exc(logging.ERROR, e, msg, *args, **kwargs)

    def warning_with_exc(self, e: Exception, msg: str = "", *args: Any, **kwargs: Any) -> None:
        """
        例外情報を含む警告ログを記録。

        Args:
            e (Exception): ログに記録する例外オブジェクト
            msg (str, optional): 追加の警告メッセージ。デフォルトは空文字列。
        """
        self._log_with_exc(logging.WARNING, e, msg, *args, **kwargs)

    def info_with_exc(self, e: Exception, msg: str = "", *args: Any, **kwargs: Any) -> None:
        """
        例外情報を含む情報ログを記録。

        Args:
            e (Exception): ログに記録する例外オブジェクト
            msg (str, optional): 追加の情報メッセージ。デフォルトは空文字列。
        """
        self._log_with_exc(logging.INFO, e, msg, *args, **kwargs)

    def _deep_repr(self, obj, max_depth=0, current_depth=0):
        """オブジェクトを再帰的に文字列に変換する。
        Args:
            obj: 変換するオブジェクト
            max_depth (int): 変換する最大の深さ
            current_depth (int): 現在の深さ
        Returns:
            str: 変換された文字列
        """
        if current_depth >= max_depth:
            return repr(obj)
        if isinstance(obj, dict):
            return {
                k: self._deep_repr(v, max_depth, current_depth+1)
                for k, v in obj.items()
            }
        elif isinstance(obj, (list, tuple)):
            return [self._deep_repr(v, max_depth, current_depth+1) for v in obj]
        elif hasattr(obj, '__dict__'):
            return {
                k: self._deep_repr(v, max_depth, current_depth+1)
                for k, v in obj.__dict__.items()
                if k in self.debug_relevant_attributes or not k.startswith('_')
            }
        else:
            return repr(obj)

    def _get_local_vars_str(self, stack_level: int = 0, max_depth: int = 0) -> str:
        """
        現在のスタックフレームからローカル変数を取得し、文字列に変換。
        Args:
            stack_level (int): 取得するスタックフレームのレベル
        """
        stack_level = stack_level + 1
        frame = inspect.stack()[stack_level][0]
        local_vars = {k: self._deep_repr(v, max_depth=max_depth) for k, v in frame.f_locals.items()}
        return f"============= LOCAL VARIABLES =============\n{pformat(local_vars)}\n==========================================="

    def log_with_stack(self, msg: str, level: int = 40, stack_level: int = 0, *args: Any, **kwargs: Any) -> None:
        """
        スタックトレースを含むログを記録(デバッグ用途を想定)
        Args:
            msg (str): ログメッセージ
            level (int): ログレベル デフォルトは40（ERROR）
            stack_level (int): スタックレベル（指定しない場合は3）
            log_local_vars (bool): ローカル変数をログに含める（デフォルトはTrue）
            depth (int): ローカル変数を展開する最大の深さ（デフォルトは1）

        Exmaple:
            >>> import logging
            >>> logger = logging.getLogger(__name__)
            >>> logger.log_with_stack("foo")  # Errorレベルのログ
            >>> logger.log_with_stack("bar", logging.INFO)  # Infoレベルのログ
        """
        stack_level = stack_level + 1
        extra = kwargs.pop('extra', {})
        extra.update(self._get_extra(stack_level))

        log_local_vars = kwargs.pop('log_local_vars', True)
        if log_local_vars:
            max_depth = kwargs.pop('depth', 1)
        local_vars = self._get_local_vars_str(stack_level=stack_level, max_depth=max_depth)
        msg = f"[DEBUG STACK TRACE] {msg}\n{local_vars}\n"

        super().log(level, f"{msg}", *args, stack_info=True, extra=extra, **kwargs)

