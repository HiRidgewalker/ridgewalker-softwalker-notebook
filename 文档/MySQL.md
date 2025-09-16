事务的四大特性: 
- 原子性 (atomicity): 事务时不可分割的最小操作单元，要么全部成，要么全部失败
- 一致性（Consistency）： 事务我弄成时，必须让所有的数据都保持一致的状态
- 隔离性（isolation）： 数据库提供的隔离机制，保证事务在不受外部并发操作影响的独立环境下运行
- 持久性 （durability）： 事务一旦提交或者回滚，它对数据库中的数据的改变是永久的

并发事务问题
- 赃读：一个事务读到另外一个事务还没有提交的数据。
	- ![[image-14.png]]
- 不可重复读：一个事务先后读取同一条记录，但两次读取的数据不同，称之为不可重复读。
	- ![[image-15.png]]
- 幻读：一个事务按照条件查询数据时，没有对应的数据行，但是在插入数据时，又发现这行数据已经存在，好像出现了 "幻影"。
	- ![[image-16.png]]

事务的隔离级别
![[image-17.png]]
> 事务隔离级别越高，数据越安全，但是性能越低。

查看和设置事务隔离级别
```sql
-- 查看事务隔离级别
SELECT @@TRANSACTION_ISOLATION;

-- 设置事务隔离级别
SET [ SESSION | GLOBAL ] TRANSACTION ISOLATION LEVEL { READ UNCOMMITTED |
READ COMMITTED | REPEATABLE READ | SERIALIZABLE }
```