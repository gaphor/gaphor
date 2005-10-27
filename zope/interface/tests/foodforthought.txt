================================
Food-based subscription examples
================================


This file gives more subscription examples using a cooking-based example::

    >>> from zope.interface.adapter import AdapterRegistry
    >>> registry = AdapterRegistry()

    >>> import zope.interface
    >>> class IAnimal(zope.interface.Interface):
    ...     pass
    >>> class IPoultry(IAnimal):
    ...     pass
    >>> class IChicken(IPoultry):
    ...     pass
    >>> class ISeafood(IAnimal):
    ...     pass

Adapting to some other interface for which there is no
subscription adapter returns an empty sequence::

    >>> class IRecipe(zope.interface.Interface):
    ...     pass
    >>> class ISausages(IRecipe):
    ...     pass
    >>> class INoodles(IRecipe):
    ...     pass
    >>> class IKFC(IRecipe):
    ...     pass

    >>> list(registry.subscriptions([IPoultry], IRecipe))
    []

unless we define a subscription::

    >>> registry.subscribe([IAnimal], ISausages, 'sausages')
    >>> list(registry.subscriptions([IPoultry], ISausages))
    ['sausages']

And define another subscription adapter::

    >>> registry.subscribe([IPoultry], INoodles, 'noodles')
    >>> meals = list(registry.subscriptions([IPoultry], IRecipe))
    >>> meals.sort()
    >>> meals
    ['noodles', 'sausages']

    >>> registry.subscribe([IChicken], IKFC, 'kfc')
    >>> meals = list(registry.subscriptions([IChicken], IRecipe))
    >>> meals.sort()
    >>> meals
    ['kfc', 'noodles', 'sausages']

And the answer for poultry hasn't changed::

    >>> meals = list(registry.subscriptions([IPoultry], IRecipe))
    >>> meals.sort()
    >>> meals
    ['noodles', 'sausages']
