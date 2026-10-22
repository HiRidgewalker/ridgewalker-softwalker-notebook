// 02 - 数组常用方法
// 对应 Hub/01_JavaScript笔记.md 第九章

const nums = [1, 2, 3, 4, 5]

// ───── 1. map / filter / reduce ─────
console.log('--- map / filter / reduce ---')

const doubled = nums.map(n => n * 2)
console.log('doubled:', doubled)                    // [2, 4, 6, 8, 10]

const evens = nums.filter(n => n % 2 === 0)
console.log('evens:', evens)                        // [2, 4]

const sum = nums.reduce((acc, n) => acc + n, 0)
console.log('sum:', sum)                            // 15

// ───── 2. find / some / every ─────
console.log('\n--- find / some / every ---')

console.log(nums.find(n => n > 3))                  // 4
console.log(nums.some(n => n > 4))                  // true
console.log(nums.every(n => n > 0))                 // true

// ───── 3. forEach vs map ─────
console.log('\n--- forEach vs map ---')

nums.forEach(n => console.log('item:', n))          // 仅遍历，无返回值
const mapped = nums.map(n => n * 10)
console.log('mapped:', mapped)                      // [10, 20, 30, 40, 50]

// ───── 4. 实战：按字段分组 ─────
console.log('\n--- 按字段分组（reduce）---')

const users = [
  { name: 'Alice', age: 18 },
  { name: 'Bob',   age: 30 },
  { name: 'Tom',   age: 18 }
]

const byAge = users.reduce((acc, u) => {
  (acc[u.age] ||= []).push(u)
  return acc
}, {})

console.log(byAge)
// → { 18: [{Alice}, {Tom}], 30: [{Bob}] }

// ───── 5. 数组去重 ─────
console.log('\n--- 数组去重 ---')

const dup = [1, 2, 2, 3, 3, 3]
console.log([...new Set(dup)])                      // [1, 2, 3]
