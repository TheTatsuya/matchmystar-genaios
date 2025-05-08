from typing import Optional
from pydantic import BaseModel


class OpenAIModel(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str


class OpenAIListModelsDTO(BaseModel):
    object: str
    data: list[Optional[OpenAIModel]] = []

    # def filter_out_non_gpt_models(self):
    #     result: list[Optional[str]] = []
    #     for model in self.data:
    #         if "gpt" in model.id or "o1" in model.id:
    #             if model.object == "model":
    #                 result.append(model.id)

    #     return {"models": result}

    def get_model_names(self):
        return [model.id for model in self.data]
