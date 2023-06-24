Prompts can be constructed chaining together YAML files.

## tag_definitions.yaml

```yaml
gpt:summary: summar_prompt.yaml
gpt:antonym: few_shot_prompt.yaml
```
## summary_prompt.yaml

```yaml
_type: prompt
input_variables:
    ["diff"]
template: |
  You are an experienced software developer.

  Generate unit test cases for the code submitted
  in the pull request, ensuring comprehensive coverage of all functions, methods,
  and scenarios to validate the correctness and reliability of the implementation.

  {diff}
```

## few_shot_prompt.yaml
```yaml
_type: few_shot
input_variables:
    ["adjective"]
prefix: 
    Write antonyms for the following words.
example_prompt:
    _type: prompt
    input_variables:
        ["input", "output"]
    template:
        "Input: {input}\nOutput: {output}"
examples:
    examples.json
suffix:
    "Input: {adjective}\nOutput:"
```

## examples.yaml
```yaml
- input: happy
  output: sad
- input: tall
  output: short
  ```
