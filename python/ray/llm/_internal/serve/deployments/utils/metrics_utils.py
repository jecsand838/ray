from typing import Optional

from ray.util.metrics import Counter

from ray.llm._internal.serve.configs.server_models import LLMRawResponse

_MODEL_ID_TAG_KEY = "model_id"
_USER_ID_TAG_KEY = "user_id"

_UNKNOWN_USER_ID_VAL = "unknown"

_METRIC_TAG_KEYS = (_MODEL_ID_TAG_KEY, _USER_ID_TAG_KEY)


class Metrics:
    def __init__(self):
        self.requests_started = Counter(
            "rayllm_requests_started",
            description="Number of requests started.",
            tag_keys=_METRIC_TAG_KEYS,
        )
        self.requests_finished = Counter(
            "rayllm_requests_finished",
            description="Number of requests finished",
            tag_keys=_METRIC_TAG_KEYS,
        )
        self.requests_errored = Counter(
            "rayllm_requests_errored",
            description="Number of requests errored",
            tag_keys=_METRIC_TAG_KEYS,
        )

        self.tokens_generated = Counter(
            "rayllm_tokens_generated",
            description="Number of tokens generated by RayLLM",
            tag_keys=_METRIC_TAG_KEYS,
        )
        self.tokens_input = Counter(
            "rayllm_tokens_input",
            description="Number of tokens input by the user",
            tag_keys=_METRIC_TAG_KEYS,
        )

    def record_request(self, *, model_id: str, user_id: str = _UNKNOWN_USER_ID_VAL):
        self.requests_started.inc(tags=self._get_tags(model_id, user_id))

    def record_input_tokens(
        self,
        input_tokens: Optional[int],
        *,
        model_id: str,
        user_id: str = _UNKNOWN_USER_ID_VAL,
    ):
        if input_tokens:
            self.tokens_input.inc(input_tokens, tags=self._get_tags(model_id, user_id))

    def record_streamed_response(
        self, res: LLMRawResponse, *, model_id: str, user_id: str = _UNKNOWN_USER_ID_VAL
    ):
        tags = self._get_tags(model_id, user_id)

        if res.num_generated_tokens:
            self.tokens_generated.inc(res.num_generated_tokens, tags=tags)

        if res.error:
            self.requests_errored.inc(tags=tags)

        if res.finish_reason is not None:
            self.requests_finished.inc(tags=tags)

    def record_failure(self, *, model_id: str, user_id: str = _UNKNOWN_USER_ID_VAL):
        self.requests_errored.inc(tags=self._get_tags(model_id, user_id))

    @staticmethod
    def _get_tags(model_id: str, user_id: str):
        return {
            _MODEL_ID_TAG_KEY: model_id,
            _USER_ID_TAG_KEY: user_id,
        }
