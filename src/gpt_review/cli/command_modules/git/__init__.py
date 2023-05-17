# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack import CLICommandsLoader

from gpt_review.cli.command_modules.git._help import helps  # pylint: disable=unused-import


class GitCommandsLoader(CLICommandsLoader):
    def __init__(self, cli_ctx=None) -> None:
        super(GitCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
        )

    def load_command_table(self, args):
        from gpt_review.cli.command_modules.git.commands import load_command_table

        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command) -> None:
        from gpt_review.cli.command_modules.git._params import load_arguments

        load_arguments(self, command)


COMMAND_LOADER_CLS = GitCommandsLoader
