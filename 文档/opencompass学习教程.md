# 数据集命名
数据集配置文件名由以下命名方式构成 `{数据集名称}_{评测方式}_{prompt版本号}.py`，以 `CLUE_afqmc/CLUE_afqmc_gen_db509b.py` 为例，该配置文件则为中文通用能力下的 `CLUE_afqmc` 数据集，对应的评测方式为 `gen`，即生成式评测，对应的prompt版本号为 `db509b`；同样的， `CLUE_afqmc_ppl_00b348.py` 指评测方式为`ppl`即判别式评测，prompt版本号为 `00b348` 。


介绍opencompass比较好的文章：
[OpenCompass傻瓜式入门教程-CSDN博客](https://blog.csdn.net/superbadguy/article/details/150431940)


opencompass官网教程
[数据分片 — OpenCompass 0.5.2 documentation](https://doc.opencompass.org.cn/zh_CN/user_guides/evaluation.html)


```shell
python run.py \
		--models api_minimax_m2_5 \
        --datasets demo_gsm8k_chat_gen \
        --work-dir eval_results/api/api_minimax_m2_5 \
        --debug

python run.py \
		--models api_minimax_m2_7 \
        --datasets demo_gsm8k_chat_gen \
        --work-dir eval_results/api/api_minimax_m2_7 \
        --debug

```

