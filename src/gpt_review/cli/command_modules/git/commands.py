# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_command_table(self, _) -> None:
    with self.command_group("git", "gpt_review._git#{}", is_preview=True) as group:
        group.command("commit", "_commit", is_preview=True)
