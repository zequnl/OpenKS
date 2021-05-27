import torch
import torch.nn as nn
from ...model import TorchModel
from typing import Callable


@TorchModel.register("NodedClassifier", "PyTorch")
class NodeClassifier(TorchModel):
    def __init__(self, node_embeddings: torch.Tensor, node_num: int) -> None:
        self.embeddings = node_embeddings
        self.embed_dim = self.embeddings.shape[1]
        self.classifier = nn.Linear(self.embed_dim, node_num)

    def forward(self, node_id: int):
        return torch.softmax(self.classifier(self.embeddings[node_id]))


@TorchModel.register("NodeMatching", "PyTorch")
class NodeMatching(TorchModel):
    def __init__(self, node_embeddings: torch.Tensor,
                 similarity_function: Callable[[torch.Tensor, torch.Tensor], torch.Tensor]=None) -> None:
        self.embeddings = node_embeddings
        self.score_func = similarity_function if similarity_function is not None else \
            lambda x, y : torch.sum(x * y) / (torch.norm(x) * torch.norm(y))

    def forward(self, id_1: int, id_2: int):
        embed_1 = self.embeddings[id_1]
        embed_2 = self.embeddings[id_2]
        return self.score_func(embed_1, embed_2)


@TorchModel.register("LinkPreiction", "PyTorch")
class LinkPrediction(TorchModel):
    def __init__(self, node_embeddings: torch.Tensor,
                 relation_embeddings: torch.Tensor,
                 entity_num: int) -> None:
        self.node_embeddings = node_embeddings
        self.relation_embeddings = relation_embeddings

    def forward(self, head_id: int, relation_id: int, tail_id: int):
        head_embed = self.node_embeddings[head_id]
        tail_embed = self.node_embeddings[tail_id]
        rel_embed = self.relation_embeddings[relation_id]
        head_scores = torch.norm(
            self.node_embeddings + rel_embed - tail_embed, dim=1)
        tail_scores = torch.norm(
            head_embed + rel_embed - self.node_embeddings, dim=1)
        return {
            "head_scores": head_scores,
            "tail_scores": tail_scores
        }


@TorchModel.register("RelationPrediction", "PyTorch")
class RelationPrediction(TorchModel):
    def __init__(self, node_embeddings: torch.Tensor,
                 relation_embeddings: torch.Tensor) -> None:
        self.node_embeddings = node_embeddings
        self.relation_embeddings = relation_embeddings
    
    def forward(self, head_id: int, tail_id: int):
        head_embed = self.node_embeddings[head_id]
        tail_embed = self.node_embeddings[tail_id]
        return torch.norm(head_embed + self.relation_embeddings - tail_embed, dim=1)
