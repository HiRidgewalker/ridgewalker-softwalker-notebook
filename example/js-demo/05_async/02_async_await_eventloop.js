// 02 - async / await 与事件循环
// 对应 Hub/03_JavaScript异步与模块笔记.md 第三、五章

// 模拟异步
const delay = (ms, value) => new Promise(r => setTimeout(() => r(value), ms))

// ───── 1. async / await 基础 ─────
console.log('--- async / await ---')

async function getUser() {
  try {
    const a = await delay(50, 'A')
    const b = await delay(50, 'B')
    return `${a} + ${b}`             // async 函数总是返回 Promise
  } catch (err) {
    console.error(err)
  }
}

getUser().then(res => console.log('结果:', res))

// ───── 2. 串行 vs 并发 ─────
console.log('\n--- 串行 vs 并发 ---')

async function serial() {
  const start = Date.now()
  await delay(100, 'x')
  await delay(100, 'y')
  console.log('  串行耗时:', Date.now() - start, 'ms')
}

async function parallel() {
  const start = Date.now()
  await Promise.all([delay(100, 'x'), delay(100, 'y')])
  console.log('  并发耗时:', Date.now() - start, 'ms')
}

serial()
parallel()

// ───── 3. 事件循环：宏任务 vs 微任务 ─────
console.log('\n--- 事件循环 ---')

console.log('1: 同步')

setTimeout(() => console.log('2: setTimeout（宏任务）'), 0)

Promise.resolve().then(() => console.log('3: Promise.then（微任务）'))

queueMicrotask(() => console.log('4: queueMicrotask（微任务）'))

console.log('5: 同步')

// 输出顺序：1 5 3 4 2
// 同步 → 微任务全部执行完 → 宏任务

// ───── 4. 经典面试题 ─────
console.log('\n--- 经典顺序题 ---')

async function async1() {
  console.log('a1 start')
  await async2()
  console.log('a1 end')              // await 后续相当于微任务
}

async function async2() {
  console.log('a2')
}

console.log('script start')

setTimeout(() => console.log('setTimeout'), 0)

async1()

new Promise(resolve => {
  console.log('promise1')
  resolve()
}).then(() => console.log('promise2'))

console.log('script end')

// 预期输出：
// script start → a1 start → a2 → promise1 → script end → a1 end → promise2 → setTimeout
