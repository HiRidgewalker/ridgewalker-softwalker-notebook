## Django ORM
Django 提供了定义三种最常见的数据库关联关系的方法：多对一，多对多，一对一。
### 多对一
定义一个多对一的关联关系，使用 [`django.db.models.ForeignKey`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ForeignKey "django.db.models.ForeignKey") 类。就和其它 [`Field`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.Field "django.db.models.Field") 字段类型一样，只需要在你模型中添加一个值为该类的属性。

[`ForeignKey`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ForeignKey "django.db.models.ForeignKey") 类需要添加一个位置参数，即你想要关联的模型类名。

例如，如果一个 `Car` 模型有一个制造者 `Manufacturer` --就是说一个 `Manufacturer` 制造许多辆车，但是每辆车都仅有一个制造者-- 那么使用下面的方法定义这个关系：

```python
from django.db import models

class Manufacturer(models.Model):
    # ...
    pass

class Car(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    # ...
```

>[!info]
>你也可以创建 [自关联关系](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#recursive-relationships) （一个模型与它本身有多对一的关系）和 [与未定义的模型间的关联关系](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#lazy-relationships) ；详情请见 [模型字段参考](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#ref-foreignkey) 。

建议设置 [`ForeignKey`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ForeignKey "django.db.models.ForeignKey") 字段名（上例中的 `manufacturer` ）为想要关联的模型名，但是你也可以随意设置为你想要的名称，例如：

```python
class Car(models.Model):
    company_that_makes_it = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
    )
    # ...
```

#### 总结
1. 多对一使用models.ForeignKey类，参数为需要关联的模型类名
2. 外键字段需要放到应用外键类上面，即`多`的一方
3. 建议外键字段名称使用类名小写

### 多对多
定义一个多对多的关联关系，使用 [`django.db.models.ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 类。就和其他 [`Field`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.Field "django.db.models.Field") 字段类型一样，只需要在你模型中添加一个值为该类的属性。

[`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 类需要添加一个位置参数，即你想要关联的模型类名。

例如：如果 `Pizza` 含有多种 `Topping` （配料） -- 也就是一种 `Topping` 可能存在于多个 `Pizza` 中，并且每个 `Pizza` 含有多种 `Topping` --那么可以这样表示这种关系：

```python
from django.db import models

class Topping(models.Model):
    # ...
    pass

class Pizza(models.Model):
    # ...
    toppings = models.ManyToManyField(Topping)
```

和 [`ForeignKey`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ForeignKey "django.db.models.ForeignKey") 类一样，你也可以创建 [自关联关系](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#recursive-relationships) （一个对象与他本身有着多对多的关系）和 [与未定义的模型的关系](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#lazy-relationships) 。

建议设置 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 字段名（上例中的 `toppings` ）为一个复数名词，表示所要关联的模型对象的集合。

对于多对多关联关系的两个模型，可以在任何一个模型中添加 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 字段，但只能选择一个模型设置该字段，即不能同时在两模型中添加该字段。

一般来讲，应该把 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 实例放到需要在表单中被编辑的对象中。在之前的例子中， `toppings` 被放在 `Pizza` 当中（而不是 `Topping` 中有指向 `pizzas` 的 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 实例 ）因为相较于配料被放在不同的披萨当中，披萨当中有很多种配料更加符合常理。按照先前说的，在编辑 `Pizza` 的表单时用户可以选择多种配料。

如要查看完整示例代码，详见 [模型多对多关联实例](https://docs.djangoproject.com/zh-hans/5.2/topics/db/examples/many_to_many/)。

[`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 字段也接受一些 [模型字段参考](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#manytomany-arguments) 中介绍的参数。这些可选的参数可以更深入地规定关联关系的具体实现。

在多对多(many-to-many)关系中添加添加额外的属性字段[¶](https://docs.djangoproject.com/zh-hans/5.2/topics/db/models/#extra-fields-on-many-to-many-relationships "Link to this heading")

如果你只是想要一个类似于记录披萨和配料之间混合和搭配的多对多关系，标准的 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 就足够你用了。但是，有时你可能需要将数据与两个模型之间的关系相关联。

举例来讲，考虑一个需要跟踪音乐人属于哪个音乐组的应用程序。在人和他们所在的组之间有一个多对多关系，你可以使用 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 来代表这个关系。然而，你想要记录更多的信息在这样的关联关系当中，比如你想要记录某人是何时加入一个组的。

对于这些情况，Django 允许你指定用于控制多对多关系的模型。你可以在中间模型当中添加额外的字段。在实例化 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 的时候使用 [`through`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField.through "django.db.models.ManyToManyField.through") 参数指定多对多关系使用哪个中间模型。对于我们举的音乐家的例子，代码如下：

```python
from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Person, through="Membership")

    def __str__(self):
        return self.name

class Membership(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "group"], name="unique_person_group"
            )
        ]
```

你需要在设置中间模型的时候，显式地为多对多关系中涉及的中间模型指定外键。这种显式声明定义了这两个模型之间是如何关联的。

If you don't want multiple associations between the same instances, add a [`UniqueConstraint`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/constraints/#django.db.models.UniqueConstraint "django.db.models.UniqueConstraint") including the `from` and `to` fields. Django's automatically generated many-to-many tables include such a constraint.

在中间模型当中有一些限制条件：

- 你的中间模型要么有且 _仅_ 有一个指向源模型（我们例子当中的 `Group` ）的外键，要么你必须通过 [`ManyToManyField.through_fields`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField.through_fields "django.db.models.ManyToManyField.through_fields") 参数在多个外键当中手动选择一个外键，如果有多个外健且没有用 `through_fields` 参数选择一个的话，会出现验证错误。对于指向目标模型（我们例子当中的 `Person` ）的外键也有同样的限制。
    
- For a model which has a many-to-many relationship to itself through an intermediary model, two foreign keys to the same model are permitted, but they will be treated as the two (different) sides of the many-to-many relationship. If [`through_fields`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField.through_fields "django.db.models.ManyToManyField.through_fields") is not specified, the first foreign key will be taken to represent the source side of the `ManyToManyField`, while the second will be taken to represent the target side. If there are _more_ than two foreign keys though, you must specify [`through_fields`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField.through_fields "django.db.models.ManyToManyField.through_fields") to explicitly indicate which foreign keys to use, otherwise a validation error will be raised.
    

现在你已经设置好了你的 [`ManyToManyField`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/#django.db.models.ManyToManyField "django.db.models.ManyToManyField") 来使用你的中介模型（在这种情况下是 `Membership`），你可以开始创建一些多对多关系。你可以通过创建中介模型的实例来实现这一点：

```python
>>> ringo = Person.objects.create(name="Ringo Starr")
>>> paul = Person.objects.create(name="Paul McCartney")
>>> beatles = Group.objects.create(name="The Beatles")
>>> m1 = Membership(
...     person=ringo,
...     group=beatles,
...     date_joined=date(1962, 8, 16),
...     invite_reason="Needed a new drummer.",
... )
>>> m1.save()
>>> beatles.members.all()
<QuerySet [<Person: Ringo Starr>]>
>>> ringo.group_set.all()
<QuerySet [<Group: The Beatles>]>
>>> m2 = Membership.objects.create(
...     person=paul,
...     group=beatles,
...     date_joined=date(1960, 8, 1),
...     invite_reason="Wanted to form a band.",
... )
>>> beatles.members.all()
<QuerySet [<Person: Ringo Starr>, <Person: Paul McCartney>]>
```

你还可以使用 [`add()`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.add "django.db.models.fields.related.RelatedManager.add")、[`create()`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.create "django.db.models.fields.related.RelatedManager.create") 或 [`set()`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.set "django.db.models.fields.related.RelatedManager.set") 来创建关系，只要为任何必需的字段指定 `through_defaults`：

```python
>>> beatles.members.add(john, through_defaults={"date_joined": date(1960, 8, 1)})
>>> beatles.members.create(
...     name="George Harrison", through_defaults={"date_joined": date(1960, 8, 1)}
... )
>>> beatles.members.set(
...     [john, paul, ringo, george], through_defaults={"date_joined": date(1960, 8, 1)}
... )
```

你可能更倾向直接创建中间模型。

如果由中介模型定义的自定义中介表不对 `(model1, model2)` 对进行唯一性强制，允许多个值，则 [`remove()`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.remove "django.db.models.fields.related.RelatedManager.remove") 调用将删除所有中介模型实例：

```python
>>> Membership.objects.create(
...     person=ringo,
...     group=beatles,
...     date_joined=date(1968, 9, 4),
...     invite_reason="You've been gone for a month and we miss you.",
... )
>>> beatles.members.all()
<QuerySet [<Person: Ringo Starr>, <Person: Paul McCartney>, <Person: Ringo Starr>]>
>>> # This deletes both of the intermediate model instances for Ringo Starr
>>> beatles.members.remove(ringo)
>>> beatles.members.all()
<QuerySet [<Person: Paul McCartney>]>
```

[`clear()`](https://docs.djangoproject.com/zh-hans/5.2/ref/models/relations/#django.db.models.fields.related.RelatedManager.clear "django.db.models.fields.related.RelatedManager.clear") 方法可以用来删除一个实例的所有多对多关系：

```python
>>> # Beatles have broken up
>>> beatles.members.clear()
>>> # Note that this deletes the intermediate model instances
>>> Membership.objects.all()
<QuerySet []>
```

一旦建立了多对多关系，你可以发出查询。与普通的多对多关系一样，你可以使用多对多相关模型的属性进行查询：

Find all the groups with a member whose name starts with 'Paul'
```python
>>> Group.objects.filter(members__name__startswith="Paul")
<QuerySet [<Group: The Beatles>]>
```

由于你使用了一个中介模型，你还可以查询它的属性：

Find all the members of the Beatles that joined after 1 Jan 1961
```python
>>> Person.objects.filter(
...     group__name="The Beatles", membership__date_joined__gt=date(1961, 1, 1)
... )
<QuerySet [<Person: Ringo Starr]>
```

如果需要访问成员信息，可以通过直接查询 `Membership` 模型来实现：

```python
>>> ringos_membership = Membership.objects.get(group=beatles, person=ringo)
>>> ringos_membership.date_joined
datetime.date(1962, 8, 16)
>>> ringos_membership.invite_reason
'Needed a new drummer.'
```

访问相同信息的另一种方式是从 `Person` 对象查询 [多对多反向关系](https://docs.djangoproject.com/zh-hans/5.2/topics/db/queries/#m2m-reverse-relationships)：

```python
>>> ringos_membership = ringo.membership_set.get(group=beatles)
>>> ringos_membership.date_joined
datetime.date(1962, 8, 16)
>>> ringos_membership.invite_reason
'Needed a new drummer.'
```
#### 总结
- 多对多关系，如果没有自定义中间模型，则在多对多的任意一方数据库类对象上添加`models.MangtomanyField()`实例
- 如果定义了中间模型，就需要注意特定的规则

### 一对一
> 很少使用，用到了再了解


### Django ORM模型字段命名限制
1. 字段名称不能是 Python 保留字，因为这会导致 Python 语法错误
2. 一个字段名称不能包含连续的多个下划线，原因在于 Django 查询语法的工作方式。比如:
	```python 
	class Example(models.Model):
    foo__bar = models.IntegerField()  # 'foo__bar' has two underscores!
	```
3. 字段名不能以下划线结尾，原因同上


### 在包中管理模型
[`manage.py startapp`](https://docs.djangoproject.com/zh-hans/5.2/ref/django-admin/#django-admin-startapp) 命令创建了一个应用结构，包含一个 `models.py` 文件。若你有很多 `models.py` 文件，用独立的文件管理它们会很实用。

为了达到此目的，创建一个 `models` 包。删除 `models.py`，创建一个 `myapp/models` 目录，包含一个 `__init__.py` 文件和存储模型的文件。你必须在 `__init__.py` 文件中导入这些模块。

比如，若你在 `models` 目录下有 `organic.py` 和 `synthetic.py`：
`myapp/models/__init__.py`[¶](https://docs.djangoproject.com/zh-hans/5.2/topics/db/models/#id11 "Link to this code")
```python
from .organic import Person
from .synthetic import Robot
```

显式导入每个模块，而不是使用 `from .models import *` 有助于不打乱命名空间，使代码更具可读性，让代码分析工具更有用。


### 模型字段类型和字段选项
[Django模型字段类型和字段选项](https://docs.djangoproject.com/zh-hans/5.2/ref/models/fields/)

### 模型meta选项
[模型Meta选项](https://docs.djangoproject.com/zh-hans/5.2/ref/models/options/)

