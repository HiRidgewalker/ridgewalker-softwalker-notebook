# Crypto 与 Web3

> 本笔记为 `文档/Crypto总结.md`、`文档/web3知识.md`、`文档/工具教程.md` 的提炼合并版。
> 原笔记保留在 `文档/` 目录下，供历史回溯。

## 一、常用公链速查

| 公链 | 浏览器 | 特点 |
|---|---|---|
| **Solana** | https://solscan.io/ | 高 TPS、低手续费，meme 币活跃地 |
| **Ethereum** | https://etherscan.io/ | 智能合约发源地，生态最丰富 |
| **BNB Chain** | https://bscscan.com/ | 币安生态，手续费低 |

## 二、核心名词速查

### 交易类

- **大宗商品（Commodities）**：同质性强、可大规模交易的商品（工业原料、能源、农产品等），价格受全球供需与地缘政治影响波动大
- **限价单**：以指定价格（或更优价格）买卖资产的订单类型
- **市价单**：按当前盘口最优价格立即成交的订单

### 心理学 / 圈层类

- **FOMO**（Fear of Missing Out）：害怕错过，看到暴涨就匆忙入场
- **KOL**（Key Opinion Leader）：关键意见领袖，观点可参考但不可作为决策依据

### 技术类

- **CA**（Contract Address）：合约地址，智能合约在区块链上的唯一标识
- **CEX**（Centralized Exchange）：中心化交易所
- **DEX**（Decentralized Exchange）：去中心化交易所

## 三、CEX vs DEX 对比

| 维度 | CEX | DEX |
|---|---|---|
| 运营方 | 中心化公司（币安、Coinbase、OKX） | 智能合约自动运行 |
| 资产托管 | 交易所托管（用户持有"欠条"） | 用户自持私钥，资产始终在钱包 |
| 撮合机制 | 订单簿（Order Book） | AMM 自动做市商 + 流动性池 |
| KYC | 必须（反洗钱合规） | 无需 |
| 法币入金 | 支持 | 不支持 |
| 优点 | 易用、流动性好、客服完善 | 无托管风险、隐私强、审查抗性高、代币上新快 |
| 缺点 | 托管风险、隐私差、监管限制 | 操作复杂、滑点风险、流动性差、缺客服 |
| 典型代表 | 币安、Coinbase、OKX | Uniswap、PancakeSwap |

## 四、网络 / 区块链 / 加密货币的区别

参考链接：https://ethereumclassic.org/zh/blog/2022-11-29-the-difference-between-a-network-a-blockchain-and-a-cryptocurrency

三者是不同层级：

- **网络（Network）**：节点组成的通信基础设施
- **区块链（Blockchain）**：运行在网络上的分布式账本技术
- **加密货币（Cryptocurrency）**：区块链上的原生资产单位

## 五、工具教程

### MetaMask 添加网络

参考视频：https://www.youtube.com/watch?v=SQJMGW3ygCk

> MetaMask 默认只接入 Ethereum 主网，添加 BSC / Polygon / Arbitrum 等网络时需要手动填入 RPC URL、Chain ID、Symbol、Explorer。

---

## 六、可复用选币速记

- **CEX 列表币**：流动性最佳，适合大资金进出
- **DEX 新币**：上线快、波动大、风险高，适合小仓位博赔率
- **合约地址（CA）核验**：任何 DEX 上的币，先去对应浏览器核实合约是否开源、是否含 mint 权限、持币集中度
