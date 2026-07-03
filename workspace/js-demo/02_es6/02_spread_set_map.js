// 02 - 展开运算符 / Set / Map / 模板字符串
// 对应 Hub/01_JavaScript笔记.md 第十二章

// ───── 1. 模板字符串 ─────
const name = 'Alice'
const age = 18
console.log(`Hello, ${name}! 今年 ${age} 岁`)

// ───── 2. 展开运算符 ─────
console.log('\n--- 展开运算符 ---')

// 数组合并
const a = [1, 2, 3]
const b = [4, 5, 6]
console.log([...a, ...b])              // [1, 2, 3, 4, 5, 6]

// 求最大 / 最小值
console.log(Math.max(...a))            // 3

// 对象浅拷贝
const obj = { x: 1, y: 2 }
const clone = { ...obj, z: 3 }
console.log(clone)                     // { x: 1, y: 2, z: 3 }

// ───── 3. Set：值唯一的集合 ─────
console.log('\n--- Set ---')

const s = new Set([1, 2, 2, 3, 3, 3])
console.log(s.size)                    // 3
console.log([...s])                    // [1, 2, 3]

s.add(4)
s.has(2)                               // true
s.delete(1)

// 数组去重
console.log([...new Set([1, 1, 2, 3])]) // [1, 2, 3]

// ───── 4. Map：任意类型的键值对 ─────
console.log('\n--- Map ---')

const m = new Map()
const keyObj = { id: 1 }

m.set('name', 'Alice')
m.set(keyObj, 'meta-data')

console.log(m.get('name'))             // Alice
console.log(m.get(keyObj))             // meta-data
console.log(m.size)                    // 2

// Map 与 Object 转换
const obj2 = { a: 1, b: 2 }
console.log(new Map(Object.entries(obj2)))   // Map(2) { 'a' => 1, 'b' => 2 }
console.log(Object.fromEntries(m))          // { name: 'Alice', '[object Object]': 'meta-data' }

// ───── 5. 可选链 + 空值合并 ─────
console.log('\n--- 可选链 + 空值合并 ---')

const user = { profile: { city: 'Beijing' } }

console.log(user?.profile?.city)       // Beijing
console.log(user?.contact?.phone)      // undefined（不报错）
console.log(user?.contact?.phone ?? '未填写')  // 未填写

// 对比 ||：0 和 '' 不会被当成「无值」
console.log(0  || 'default')           // default
console.log(0  ?? 'default')           // 0
console.log('' || 'default')           // default
console.log('' ?? 'default')           // ''
