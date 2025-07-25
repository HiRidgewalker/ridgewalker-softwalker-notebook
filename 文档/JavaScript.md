## JavaScript短路运算符的详解
### ✅ 一、逻辑或 `||`：返回第一个 truthy 值，或最后一个 falsy 值

```javascript
let a = 0 || "hello"; console.log(a); // "hello"  
let b = "" || 0 || false || "yes"; console.log(b); // "yes"  
let c = null || undefined || 0; console.log(c); // 0
```

**总结**：

- 一路从左往右找 truthy，第一个找到的 truthy 就是返回值；
    
- 如果全是 falsy，返回最后一个。
    

---


✅ 二、逻辑与 `&&`：返回第一个 falsy 值，或最后一个 truthy 值

```javascript
let a = 1 && "hello"; console.log(a); // "hello"  
let b = 1 && true && "" && "yes"; console.log(b); // ""（第一个 falsy）  
let c = "abc" && 123 && true; console.log(c); // true
```

**总结**：

- 一路从左往右找 falsy，第一个找到的 falsy 就是返回值；
    
- 如果全是 truthy，返回最后一个。
    

---

✅ 三、结合赋值语句：左值赋的是谁？
逻辑或 `||`：
```javascript
let a; let input = "";  
a = input || "默认值"; 
console.log(a); // "默认值"
```

逻辑与 `&&`：
```javascript
let a; let user = "小明";  
a = user && "已登录"; 
console.log(a); // "已登录"
```


---


✅ 四、真实用途举例

1. 设置默认值：

```javascript
let name = userInput || "游客"; // userInput 为空时使用“游客”
```

2. 条件执行：
```javascript
isAdmin && showAdminPanel(); // 只有管理员才执行函数
```

---

✅ 返回值总结表格：

| 表达式            | 结果    | 说明               |
| -------------- | ----- | ---------------- |
| `0`            |       | "hi"`            |
| `false`        |       | null`            |
| `"abc" && 123` | `123` | 全为 truthy，返回最后一个 |
| `"abc" && 0`   | `0`   | 返回第一个 falsy      |
