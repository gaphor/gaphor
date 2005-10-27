==========
Интерфейсы
==========

.. contents::

Интерфейсы - это объекты специфицирующие (документирующие) внешнее поведение
объектов которые их "предоставляют". Интерфейсы определяют поведение через
следующие составляющие:

- Неформальную документацию в строках документации

- Определения атрибутов

- Инварианты, представленные условиями которые должны быть соблюдены
  для объектов предоставляющих интерфейс

Определения атрибутов описывают конкретные атрибуты. Они определяют
имя атрибута и предоставляют документацию и ограничения для значений
атрибута. Определения атрибутов могут быть заданы несколькими путями
как мы увидим ниже.

Определение интерфейсов
=======================

Интерфейсы определяются с использованием ключевого слова class:

  >>> import zope.interface
  >>> class IFoo(zope.interface.Interface):
  ...    """Foo blah blah"""
  ...
  ...    x = zope.interface.Attribute("""X blah blah""")
  ...
  ...    def bar(q, r=None):
  ...        """bar blah blah"""

В примере выше мы создали интерфейс `IFoo`. Мы наследуем его от
класса `zope.interface.Interface`, который является родительским интерфейсом
для всех интерфейсов, как `object` - это родительский класс для всех новых
классов [#create]_. Данный интерфейс не является классом, а является
Интерфейсом, экземпляром `InterfaceClass`::

  >>> type(IFoo)
  <class 'zope.interface.interface.InterfaceClass'>
  
Мы можем запросить у интерфейса его документацию::

  >>> IFoo.__doc__
  'Foo blah blah'

и его имя::

  >>> IFoo.__name__
  'IFoo'

и даже модуль в котором он определен::

  >>> IFoo.__module__
  '__main__'

Наш интерфейс определяет два атрибута:

`x`
  Это простейшая форма определения атрибутов. Определяются имя
  и строка документации. Формально здесь не определяется ничего более.

`bar`
  Это метод. Методы определяются как обычные функции. Метод - это просто
  атрибут который должен быть вызываемым с указанием сигнатуры,
  предоставляемой определением функции.

  Надо отметить, что аргумент `self` не указывается для `bar`. Интерфейс
  документирует как объект *используется*. Когда методы экземпляров классов
  вызываются мы не передаем аргумент `self`, таким образом аргумент `self`
  не включается и в сигнатуру интерфейса. Аргумент `self` в методах
  экземпляров классов на самом деле деталь реализации экземпляров классов
  в Python. Другие объекты кроме экземпляров классов могут предоставлять
  интерфейсы и их методы могут не быть методами экземпляров классов. Для
  примера модули могут предоставлять интерфейсы и их методы обычно просто
  функции. Даже экземпляры могут иметь методы не являющиеся методами
  экземпляров класса.

Мы можем получить доступ к атрибутам определенным интерфейсом используя
синтакс доступа к элементам массива::

  >>> x = IFoo['x']
  >>> type(x)
  <class 'zope.interface.interface.Attribute'>
  >>> x.__name__
  'x'
  >>> x.__doc__
  'X blah blah'

  >>> IFoo.get('x').__name__
  'x'

  >>> IFoo.get('y')

Можно использовать `in` для определения содержит ли интерфейс
определенное имя::

  >>> 'x' in IFoo
  True

Мы можем использовать итератор для интерфейсов что бы получить все имена
которые интерфейсы определяют::

  >>> names = list(IFoo)
  >>> names.sort()
  >>> names
  ['bar', 'x']

Надо помнить, что интерфейсы не являются классами. Мы не можем получить
доступ к определениям атрибутов через доступ к атрибутам интерфейсов::

  >>> IFoo.x
  Traceback (most recent call last):
    File "<stdin>", line 1, in ?
  AttributeError: 'InterfaceClass' object has no attribute 'x'

Методы также предоставляют доступ к сигнатуре метода::

  >>> bar = IFoo['bar']
  >>> bar.getSignatureString()
  '(q, r=None)'

  (Методы должны иметь лучший API. Это то, что должно быть улучшено.)

Объявление интерфейсов
======================

Определив интерфес мы можем теперь *объявить*, что объекты предоставляют их.
Перед описанием деталей определим некоторые термины:

*предоставлять*
  Мы говорим, что объекты *предоставляют* интерфейсы. Если объект
  предоставляет интерфейс, тогда интерфейс специфицирует поведение объекта.
  Другими словами, интерфейсы специфицируют поведение объектов которые
  предоставляют их.

*реализовать*
  Мы обычно говорим что классы *реализуют* интерфейсы. Если класс
  реализует интерфейс, тогда экземпляры этого класса предоставляют
  данный интерфейс. Объекты предоставляют интерфейсы которые их классы
  реализуют [#factory]_. (Объекты также могут предоставлять интерфейсы напрямую
  плюс к тем которые реализуют их классы.)

  Важно помнить, что классы обычно не предоставляют интерфейсы которые
  они реализуют.

  Мы можем обобщить это до фабрик. Для любого вызываемого объекта мы можем
  объявить что он производит объекты которые предоставляют какие-либо
  интерфейсы сказав, что фабрика реализует данные интерфейсы.

Теперь после того как мы определили эти термины мы можем поговорить об
API для объявления интерфейсов.

Обявление реализуемых интерфесов
--------------------------------

Наиболее часто используемый путь для объявления интерфейсов - это использование
функции implements в определении класса::

  >>> class Foo:
  ...     zope.interface.implements(IFoo)
  ...
  ...     def __init__(self, x=None):
  ...         self.x = x
  ...
  ...     def bar(self, q, r=None):
  ...         return q, r, self.x
  ...
  ...     def __repr__(self):
  ...         return "Foo(%s)" % self.x

В этом примере мы объявили, что `Foo` реализует `IFoo`. Это значит, что
экземпляры `Foo` предоставляют `IFoo`. После данного объявления есть
несколько путей для анализа объявлений. Во-первых мы можем спросить
что интерфейс реализован классом::

  >>> IFoo.implementedBy(Foo)
  True

Также мы можем спросить если интерфейс предоставляется объектами класса::

  >>> foo = Foo()
  >>> IFoo.providedBy(foo)
  True

Конечно `Foo` не предоставляет `IFoo`, он реализует его::

  >>> IFoo.providedBy(Foo)
  False

Мы можем также узнать какие интерфейсы реализуются объектами::

  >>> list(zope.interface.implementedBy(Foo))
  [<InterfaceClass __main__.IFoo>]

Это ошибка спрашивать про интерфейсы реализуемые невызываемым объектом::

  >>> IFoo.implementedBy(foo)
  Traceback (most recent call last):
  ...
  TypeError: ('ImplementedBy called for non-factory', Foo(None))

  >>> list(zope.interface.implementedBy(foo))
  Traceback (most recent call last):
  ...
  TypeError: ('ImplementedBy called for non-factory', Foo(None))

Также можно узнать какие интерфейсы предоставляются объектами::

  >>> list(zope.interface.providedBy(foo))
  [<InterfaceClass __main__.IFoo>]
  >>> list(zope.interface.providedBy(Foo))
  []

Мы можем объявить интерфейсы реализуемые другими фабриками (кроме классов).
Это можно сделать используя декоратор `implementer` (в стиле Python 2.4).
Для версий Python ниже 2.4 это будет выглядеть следующим образом:

  >>> def yfoo(y):
  ...     foo = Foo()
  ...     foo.y = y
  ...     return foo
  >>> yfoo = zope.interface.implementer(IFoo)(yfoo)

  >>> list(zope.interface.implementedBy(yfoo))
  [<InterfaceClass __main__.IFoo>]

Надо заметить, что декоратор implementer может модифицировать свои аргументы.
Вызывающая сторона не должна предполагать, что всегда будет создаваться
новый объект.

Также надо отметить, что как минимум сейчас implementer не может использоваться
для классов:

  >>> zope.interface.implementer(IFoo)(Foo)
  ... # doctest: +NORMALIZE_WHITESPACE
  Traceback (most recent call last):
    ...
  TypeError: Can't use implementer with classes.  
  Use one of the class-declaration functions instead.

Объявление предоставляемых интерфейсов
--------------------------------------

Мы можем объявлять интерфейсы напрямую предоставляемые объектами. Предположим
что мы хотим документировать что делает метод `__init__` класса `Foo`. Это
*точно* не часть `IFoo`. Обычно мы не должны напрямую вызывать метод `__init__`
для экземпляров Foo. Скорее метод `__init__` является частью метода `__call__`
класса `Foo`::

  >>> class IFooFactory(zope.interface.Interface):
  ...     """Create foos"""
  ...
  ...     def __call__(x=None):
  ...         """Create a foo
  ...
  ...         The argument provides the initial value for x ...
  ...         """

У нас есть класс предоставляющий данный интерфейс, таким образом мы можем
объявить интерфейс класса::

  >>> zope.interface.directlyProvides(Foo, IFooFactory)

Теперь мы видим, что Foo уже предоставляет интерфейсы::

  >>> list(zope.interface.providedBy(Foo))
  [<InterfaceClass __main__.IFooFactory>]
  >>> IFooFactory.providedBy(Foo)
  True

Объявление интерфейсов класса достаточно частая операция и для нее есть
специальная функция объявления `classProvides`, которая позволяет объявлять
интерфейсы при определении класса::

  >>> class Foo2:
  ...     zope.interface.implements(IFoo)
  ...     zope.interface.classProvides(IFooFactory)
  ...
  ...     def __init__(self, x=None):
  ...         self.x = x
  ...
  ...     def bar(self, q, r=None):
  ...         return q, r, self.x
  ...
  ...     def __repr__(self):
  ...         return "Foo(%s)" % self.x

  >>> list(zope.interface.providedBy(Foo2))
  [<InterfaceClass __main__.IFooFactory>]
  >>> IFooFactory.providedBy(Foo2)
  True

Похожая функция `moduleProvides` поддерживает объявление интерфейсов при
определении модуля. Для примера смотрите использование вызова
`moduleProvides` в `zope.interface.__init__`, который объявляет, что
пакет `zope.interface` предоставляет `IInterfaceDeclaration`.

Иногда мы хотим объявить интерфейсы экземпляров, даже если эти экземпляры
уже берут интерфейсы от своих классов. Предположим, что мы создаем новый
интерфейс `ISpecial`::

  >>> class ISpecial(zope.interface.Interface):
  ...     reason = zope.interface.Attribute("Reason why we're special")
  ...     def brag():
  ...         "Brag about being special"

Мы можем сделать созданный экземпляр foo специальным предоставив атрибуты
`reason` и `brag`::

  >>> foo.reason = 'I just am'
  >>> def brag():
  ...      return "I'm special!"
  >>> foo.brag = brag
  >>> foo.reason
  'I just am'
  >>> foo.brag()
  "I'm special!"

и объявив интерфейс::

  >>> zope.interface.directlyProvides(foo, ISpecial)

таким образом новый интерфейс включается в список предоставляемых интерфейсов::

  >>> ISpecial.providedBy(foo)
  True
  >>> list(zope.interface.providedBy(foo))
  [<InterfaceClass __main__.ISpecial>, <InterfaceClass __main__.IFoo>]

Мы также можем определить, что интерфейсы напрямую предоставляются
объектами::

  >>> list(zope.interface.directlyProvidedBy(foo))
  [<InterfaceClass __main__.ISpecial>]

  >>> newfoo = Foo()
  >>> list(zope.interface.directlyProvidedBy(newfoo))
  []

Наследуемые объявления
----------------------

Обычно объявления наследуются::

  >>> class SpecialFoo(Foo):
  ...     zope.interface.implements(ISpecial)
  ...     reason = 'I just am'
  ...     def brag(self):
  ...         return "I'm special because %s" % self.reason

  >>> list(zope.interface.implementedBy(SpecialFoo))
  [<InterfaceClass __main__.ISpecial>, <InterfaceClass __main__.IFoo>]

  >>> list(zope.interface.providedBy(SpecialFoo()))
  [<InterfaceClass __main__.ISpecial>, <InterfaceClass __main__.IFoo>]

Иногда мы не хотим наследовать объявления. В этом случае мы можем
использовать `implementsOnly` вместо `implements`::

  >>> class Special(Foo):
  ...     zope.interface.implementsOnly(ISpecial)
  ...     reason = 'I just am'
  ...     def brag(self):
  ...         return "I'm special because %s" % self.reason

  >>> list(zope.interface.implementedBy(Special))
  [<InterfaceClass __main__.ISpecial>]

  >>> list(zope.interface.providedBy(Special()))
  [<InterfaceClass __main__.ISpecial>]

Внешние объявления
------------------

Обычно мы создаем объявления реализации как часть объявления класса. Иногда
мы можем захотеть создать объявления вне объявления класса. Для примера,
мы можем хотеть объявить интерфейсы для классов которые писали не мы.
Для этого может использоваться функция `classImplements`::

  >>> class C:
  ...     pass

  >>> zope.interface.classImplements(C, IFoo)
  >>> list(zope.interface.implementedBy(C))
  [<InterfaceClass __main__.IFoo>]

Мы можем использовать `classImplementsOnly` для исключения наследуемых
интерфейсов::

  >>> class C(Foo):
  ...     pass

  >>> zope.interface.classImplementsOnly(C, ISpecial)
  >>> list(zope.interface.implementedBy(C))
  [<InterfaceClass __main__.ISpecial>]

Объекты объявлений
------------------

Когда мы объявляем интерфейсы мы создаем объект *объявления*. Когда мы
запрашиваем объявления возвращается объект объявления::

  >>> type(zope.interface.implementedBy(Special))
  <class 'zope.interface.declarations.Implements'>

Объекты объявления и объекты интерфейсов во многом похожи друг на друга.
На самом деле они даже имеют общий базовый класс. Важно понять, что они могут
использоваться там где в объявлениях ожидаются интерфейсы. Вот простой
пример::

  >>> class Special2(Foo):
  ...     zope.interface.implementsOnly(
  ...          zope.interface.implementedBy(Foo),
  ...          ISpecial,
  ...          )
  ...     reason = 'I just am'
  ...     def brag(self):
  ...         return "I'm special because %s" % self.reason

Объявление здесь практически такое же как
``zope.interface.implements(ISpecial)``, отличие только в порядке
интерфейсов в итоговом объявления::

  >>> list(zope.interface.implementedBy(Special2))
  [<InterfaceClass __main__.IFoo>, <InterfaceClass __main__.ISpecial>]

Наследование интерфейсов
========================

Интерфейсы могут расширять другие интерфейсы. Они делают это просто
показывая эти интерфейсы как базовые::

  >>> class IBlat(zope.interface.Interface):
  ...     """Blat blah blah"""
  ...
  ...     y = zope.interface.Attribute("y blah blah")
  ...     def eek():
  ...         """eek blah blah"""

  >>> IBlat.__bases__
  (<InterfaceClass zope.interface.Interface>,)

  >>> class IBaz(IFoo, IBlat):
  ...     """Baz blah"""
  ...     def eek(a=1):
  ...         """eek in baz blah"""
  ...

  >>> IBaz.__bases__
  (<InterfaceClass __main__.IFoo>, <InterfaceClass __main__.IBlat>)

  >>> names = list(IBaz)
  >>> names.sort()
  >>> names
  ['bar', 'eek', 'x', 'y']

Заметим, что `IBaz` переопределяет eek::

  >>> IBlat['eek'].__doc__
  'eek blah blah'
  >>> IBaz['eek'].__doc__
  'eek in baz blah'

Мы были осторожны переопределяя eek совместимым путем. Когда интерфейс
расширяется, расширенный интерфейс должен быть совместимым [#compat]_ с
расширяемыми интерфейсами.

Мы можем запросить расширяет ли один из интерфейсов другой::

  >>> IBaz.extends(IFoo)
  True
  >>> IBlat.extends(IFoo)
  False

Заметим, что интерфейсы не расширяют сами себя::

  >>> IBaz.extends(IBaz)
  False

Иногда мы можем хотеть что бы они расширяли сами себя, но вместо этого
мы можем использовать `isOrExtends`::

  >>> IBaz.isOrExtends(IBaz)
  True
  >>> IBaz.isOrExtends(IFoo)
  True
  >>> IFoo.isOrExtends(IBaz)
  False

Когда мы применяем итерацию к интерфесу мы получаем все имена которые он
определяет включая имена определенные для базовых интерфесов. Иногда
мы хотим получить *только* имена определенные интерфейсом напрямую.
Для этого мы используем метод `names`::

  >>> list(IBaz.names())
  ['eek']

Наследование в случае определения атрибутов
--------------------------------------------

Интерфейс может переопределять определения атрибутов из базовых интерфейсов.
Если два базовых интерфейса определяют один и тот же атрибут атрибут
наследуется от более специфичного интерфейса. Для примера:

  >>> class IBase(zope.interface.Interface):
  ...
  ...     def foo():
  ...         "base foo doc"

  >>> class IBase1(IBase):
  ...     pass

  >>> class IBase2(IBase):
  ...
  ...     def foo():
  ...         "base2 foo doc"

  >>> class ISub(IBase1, IBase2):
  ...     pass

Определение ISub для foo будет из IBase2 т.к. IBase2 более специфичен для
IBase:

  >>> ISub['foo'].__doc__
  'base2 foo doc'

Заметим, что это отличается от поиска в глубину.

Иногда полезно узнать, что интерфейс определяет атрибут напрямую. Мы можем
использовать метод direct для получения напрямую определенных атрибутов:

  >>> IBase.direct('foo').__doc__
  'base foo doc'

  >>> ISub.direct('foo')

Спецификации
------------

Интерфейсы и объявления - это специальные случаи спецификаций. Описание
выше для наследования интерфейсов можно применить и к объявлениям и
к спецификациям. Объявления фактически расширяют интерфейсы которые они
объявляют:

  >>> class Baz:
  ...     zope.interface.implements(IBaz)

  >>> baz_implements = zope.interface.implementedBy(Baz)
  >>> baz_implements.__bases__
  (<InterfaceClass __main__.IBaz>,)

  >>> baz_implements.extends(IFoo)
  True

  >>> baz_implements.isOrExtends(IFoo)
  True
  >>> baz_implements.isOrExtends(baz_implements)
  True

Спецификации (интерфейсы и объявления) предоставляют атрибут `__sro__`
который описывает спецификацию и всех ее предков:

  >>> baz_implements.__sro__
  (<implementedBy __main__.Baz>,
   <InterfaceClass __main__.IBaz>,
   <InterfaceClass __main__.IFoo>,
   <InterfaceClass __main__.IBlat>,
   <InterfaceClass zope.interface.Interface>)

Помеченные значения
===================

Интерфейсы и описания атрибутов поддерживают механизм расширения
заимствованный из UML и называемый "помеченные значения" который позволяет
сохранять дополнительные данные::

  >>> IFoo.setTaggedValue('date-modified', '2004-04-01')
  >>> IFoo.setTaggedValue('author', 'Jim Fulton')
  >>> IFoo.getTaggedValue('date-modified')
  '2004-04-01'
  >>> IFoo.queryTaggedValue('date-modified')
  '2004-04-01'
  >>> IFoo.queryTaggedValue('datemodified')
  >>> tags = list(IFoo.getTaggedValueTags())
  >>> tags.sort()
  >>> tags
  ['author', 'date-modified']

Атрибуты функций конвертируются в помеченные значения когда создаются
определения атрибутов метода::

  >>> class IBazFactory(zope.interface.Interface):
  ...     def __call__():
  ...         "create one"
  ...     __call__.return_type = IBaz

  >>> IBazFactory['__call__'].getTaggedValue('return_type')
  <InterfaceClass __main__.IBaz>

Инварианты
==========

Интерфейсы могут описывать условия которые должны быть соблюдены для объектов
которые их предоставляют. Эти условия описываются используя один или более
инвариантов. Инварианты - это вызываемые объекты которые будут вызваны
с объектом предоставляющим интерфейс в качестве параметра. Инвариант
должен выкинуть исключение `Invalid` если условие не соблюдено. Например::

  >>> class RangeError(zope.interface.Invalid):
  ...     """A range has invalid limits"""
  ...     def __repr__(self):
  ...         return "RangeError(%r)" % self.args

  >>> def range_invariant(ob):
  ...     if ob.max < ob.min:
  ...         raise RangeError(ob)

Определив этот инвариант мы можем использовать его в определении интерфейсов::

  >>> class IRange(zope.interface.Interface):
  ...     min = zope.interface.Attribute("Lower bound")
  ...     max = zope.interface.Attribute("Upper bound")
  ...
  ...     zope.interface.invariant(range_invariant)

Интерфейсы имеют метод для проверки своих инвариантов::

  >>> class Range(object):
  ...     zope.interface.implements(IRange)
  ...
  ...     def __init__(self, min, max):
  ...         self.min, self.max = min, max
  ...
  ...     def __repr__(self):
  ...         return "Range(%s, %s)" % (self.min, self.max)

  >>> IRange.validateInvariants(Range(1,2))
  >>> IRange.validateInvariants(Range(1,1))
  >>> IRange.validateInvariants(Range(2,1))
  Traceback (most recent call last):
  ...
  RangeError: Range(2, 1)

В случае нескольких инвариантов мы можем захотеть остановить проверку после
первой ошибки. Если мы передадим в `validateInvariants` пустой список тогда
будет выкинуто единственное исключение `Invalid` со списком исключений
как аргументом::

  >>> errors = []
  >>> IRange.validateInvariants(Range(2,1), errors)
  Traceback (most recent call last):
  ...
  Invalid: [RangeError(Range(2, 1))]

И список будет заполнен индивидуальными исключениями::

  >>> errors
  [RangeError(Range(2, 1))]


.. [#create] Основная причина по которой мы наследуемся от `Interface` - это
             что бы быть уверенными в том, что ключевое слово class будет
             создавать интерфейс, а не класс.

             Есть возможность создать интерфейсы вызвав специальный
             класс интерфейса напрямую. Делая это, возможно (и в редких
             случаях полезно) создать интерфейсы которые не наследуются
             от `Interface`. Однако использование этой техники выходит
	     за рамки данного документа.

.. [#factory] Классы - это фабрики. Они могут быть вызваны для создания
              своих экземпляров. Мы ожидаем что в итоге мы расширим
              концепцию реализации на другие типы фабрик, таким образом
              мы сможем объявлять интерфейсы предоставляемые созданными
              фабриками объектами.

.. [#compat] Цель - заменяемость. Объект который предоставляет расширенный
             интерфейс должен быть заменяем в качестве объектов которые
             предоставляют расширяемый интерфейс. В нашем примере объект
             который предоставляет IBaz должен быть используемым и
             в случае если ожидается объект который предоставляет IBlat.

             Реализация интерфейса не требует этого. Но возможно в дальнейшем
             она должна будет делать какие-либо проверки.
