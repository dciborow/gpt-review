# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.help_files import helps


helps[
    "github"
] = """
type: group
short-summary: Use GPT with GitHub Repositories.
"""

helps[
    "github review"
] = """
type: command
short-summary: Review GitHub PR with Open AI, and post response as a comment.
"""
