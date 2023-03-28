from external import pyanvil

with pyanvil.World(r'C:\Users\Vadik\AppData\Roaming\.minecraft\saves\New World') as world:
    block = world.get_block((45, 3, 111))
    block.set_state(pyanvil.BlockState('minecraft:gold_ore', {}))
    print(block)





