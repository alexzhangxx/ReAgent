#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.

import torch
from reagent.models.base import ModelBase


class BatchConstrainedDQN(ModelBase):
    def __init__(
        self, state_dim, q_network, imitator_network, bcq_drop_threshold
    ) -> None:
        super().__init__()
        assert state_dim > 0, "state_dim must be > 0, got {}".format(state_dim)
        self.state_dim = state_dim
        self.q_network = q_network
        self.imitator_network = imitator_network
        self.invalid_action_penalty = -1e10
        self.bcq_drop_threshold = bcq_drop_threshold

    def input_prototype(self):
        return self.q_network.input_prototype()

    def forward(self, state):
        q_values = self.q_network(state)
        imitator_outputs = self.imitator_network(state.float_features)
        imitator_probs = torch.nn.functional.softmax(imitator_outputs, dim=1)
        filter_values = imitator_probs / imitator_probs.max(keepdim=True, dim=1)[0]
        invalid_actions = (filter_values < self.bcq_drop_threshold).float()
        invalid_action_penalty = self.invalid_action_penalty * invalid_actions
        constrained_q_values = q_values + invalid_action_penalty
        return constrained_q_values
