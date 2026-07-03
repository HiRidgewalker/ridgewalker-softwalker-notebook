// 01 - Promise 基础与链式调用
// 对应 Hub/03_JavaScript异步与模块笔记.md 第四章

// 模拟异步操作
function fetchData(url, shouldFail = false) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (shouldFail) reject(new Error(`请求失败: ${url}`))
      else resolve({ url, data: `mock-data-for-${url}` })
    }, 100)
  })
}

// ───── 1. 基本用法 ─────
console.log('--- 基本用法 ---')

fetchData('/api/user')
  .then(res => {
    console.log('1:', res)
    return fetchData(`/api/posts/${res.url}`)
  })
  .then(res => {
    console.log('2:', res)
  })
  .catch(err => {
    console.error('错误:', err.message)
  })
  .finally(() => {
    console.log('done')
  })

// ───── 2. Promise.all ─────
console.log('\n--- Promise.all ---')

Promise.all([
  fetchData('/api/a'),
  fetchData('/api/b'),
  fetchData('/api/c')
])
  .then(results => {
    console.log('all success:', results.length, '个请求')
  })
  .catch(err => {
    console.error('任一失败:', err.message)
  })

// ───── 3. Promise.allSettled ─────
console.log('\n--- Promise.allSettled ---')

Promise.allSettled([
  fetchData('/api/a'),
  fetchData('/api/b', true),       // 这个会失败
  fetchData('/api/c')
]).then(results => {
  results.forEach(r => {
    if (r.status === 'fulfilled') console.log('  ✓', r.value.url)
    else                          console.log('  ✗', r.reason.message)
  })
})

// ───── 4. Promise.race ─────
console.log('\n--- Promise.race ---')

Promise.race([
  fetchData('/api/fast', false),
  fetchData('/api/slow', false)
]).then(res => {
  console.log('最快完成的:', res.url)
})
