# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _) -> None:
    with self.argument_context("git commit") as args:
        args.argument(
            "gpt4",
            help="Use gpt-4 for generating commit messages instead of gpt-35-turbo.",
            default=False,
            action="store_true",
        )
        args.argument(
            "large",
            help="Use gpt-4-32k model for generating commit messages.",
            default=False,
            action="store_true",
        )
        args.argument(
            "push",
            help="Push the commit to the remote.",
            default=False,
            action="store_true",
        )
