提取试卷中题目（非题组）
```
你的任务是从Markdown格式的试卷中提取选择题题目，并以特定JSON格式输出。需处理试卷顶部或底部可能存在的题目缺失情况。  
### 试卷内容  
该部分内容由用户输入，具体如下：  
<test_paper_content>  
{{TEST_PAPER_CONTENT}}  
</test_paper_content>  
  
### 顶部缺失题目补充内容  
若试卷顶部题目缺失，以下补充内容由用户提供：  
<top_incomplete_question_replenish_content>  
{{TOP_INCOMPLETE_QUESTION_REPLENISH_CONTENT}}  
</top_incomplete_question_replenish_content>  
  
### 提取题目规则  
1. 结合试卷内容与顶部缺失题目补充内容进行题目提取。  
2. 针对每个题目，提取题目前面的ID（int类型）、题目描述及题目的选项。  
3. 若底部题目缺失, 缺失标准参考**4**，将缺失的题目内容放入JSON中的"bottom_incomplete_question_content"字段；若没有缺失，该字段返回空字符串，以保证JSON结构统一。  
4. **正常题目和异常题目的评判标准**：正常题目有两种情况，第一种是必须同时具备题目描述（题干）和题目的选项，且题目的选项有ABCD四个选项，同时语义完整，符合常规理解习惯；第二种是题目的题干后紧跟![image](图片链接)。若不满足这些条件，则视为题目缺失。  
5. 严格以JSON格式返回。  
6. 输出须为合法的JSON格式。最终的JSON输出放在<json_output>标签内。  
  
### 输出格式  
<json_output>  
{  
    "question": [        {            "id": 题目前面的id,  
            "content": 题目描述以及题目的选项  
            "options": ["选项A", "选项B", "选项C", "选项D"]   
        }  
    ],    "bottom_incomplete_question_content": "question_id. question_content"}  
</json_output>  
#### 输出格式补充说明  
- 如果在题目的题目内容中没有看到选项ABCD, 则"options"字段默认填写: ["A", "B", "C", "D"], 否则填充题目选项

```

题组
```
你的任务是解析一张markdown结构的试题试卷，将试卷内容整理成指定的JSON格式，并将json数据放入<output></output>标签中。试卷中的题目特点是每个大题包含一个大题题干和若干道小题，回答小题需要结合大题的题干。每次提供的试题内容可能存在顶部内容缺失或底部内容缺失，试题题目是否缺失见###试题结构判断完整标准  
  
### 试卷内容  
该部分内容由用户输入，具体如下：  
<test_paper_content>  
{{TEST_PAPER_CONTENT}}  
</test_paper_content>  
  
### 顶部缺失题目补充内容  
若试卷顶部题目缺失，以下补充内容由用户提供：  
<top_incomplete_question_replenish_content>  
{{TOP_INCOMPLETE_QUESTION_REPLENISH_CONTENT}}  
</top_incomplete_question_replenish_content>  
  
### 试题结构判断完整标准  
1. 大题题干语义完整，符合完整的阅读语义  
2. 大题包含的小题有5道或者10道，少一道都属于试卷缺失  
  
请按照以下步骤解析试卷：  
3. 先将第一页头部缺失的内容补充到试卷内容开头。  
4. 识别出每个大题的题干和其包含的小题，参考完整题型的评判标准###试题结构判断完整标准  
5. 每个小题的id为小题前面的题目序号  
6. 整理每个大题和小题的内容，整理小题内容时，要同时包含小题的题干描述和选项信息。  
7. 若某个大题不完整（即小题数量不足5道或者10道），则不将该大题放入"question"字段中，仅将不完整的大题内容（包含该大题内的小题）放到返回的JSON的"bottom_incomplete_question_content"字段中。  
  
### 输出JSON格式  
{

    "question": [

        {

            "parent_question": {

                "parent_question_content": "大题题干内容",

                "child_question": [

                    {

                        "child_question_id": 1,

                        "child_question_content": "小题内容（题干描述）",

                        "child_question_options": ["选项A", "选项B", "选项C", "选项D"],

                    }

                ],

            }

        }

    ],

    "bottom_incomplete_question_content": "底部不完整的大题内容(包含该大题内的小题)",
}
#### 输出格式补充说明  
- 如果在小题题目的题目内容中没有选项ABCD, 则"options"字段默认填写: ["A", "B", "C", "D"], 否则填充题目选项  
请仔细检查<test_paper_content>标签内的底部内容，如果存在整个大题不完整的情况，将其放到返回的JSON的"bottom_incomplete_question_content"字段中。  
  
请在<output></output>标签中存放输出的json数据
```

答案解析
```txt
你的任务是处理试卷答案解析，具体步骤如下：
1. 接收用户提供的<answer_analysis_content>和<top_incomplete_question_replenish_content>。其中，<top_incomplete_question_replenish_content>若不为空，它是对<answer_analysis_content>顶部残缺内容的补充；若为空，则表示<answer_analysis_content>顶部内容不残缺。
    - <answer_analysis_content>内容为：{{ANSWER_ANALYSIS}}
    - <top_incomplete_question_replenish_content>内容为：{{TOP_INCOMPLETE_QUESTION_REPLENISH_CONTENT}}
2. 检查<answer_analysis_content>底部内容是否缺失，判断依据是底部结束处语义是否完整。若存在缺失，将该缺失语义所属答案内容原封不动地填充到 "bottom_incomplete_question_content" 中，且不将该缺失语义的答案提取到 "analysis_data" 字段的数组中。
3. 从答案解析中提取题目序号、正确答案和题目解析，构建一个 JSON 对象。JSON 对象的结构必须严格按照以下格式：
{
    "analysis_data": [
        {
            "question_number": 答案前面的序号,  // 此数据类型为 int
            "question_true_answer": 正确答案，正确答案只能是 A, B, C, D, E 中的一个,  // 此数据类型为 string
            "question_analysis": 题目解析,如果对应题号的答案没有解析则填写: "" （解释: 空字符）  // 此数据类型为 string
        }
    ],
    "bottom_incomplete_question_content": ""
}
4. 最终，在<output>标签内输出提取后的 JSON 数据。
<output>
[在此输出 JSON 数据]
</output>

```