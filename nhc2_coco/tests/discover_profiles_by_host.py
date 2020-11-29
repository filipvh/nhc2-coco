import asyncio

from nhc2_coco.coco_discover_profiles import CoCoDiscoverProfiles

disc = CoCoDiscoverProfiles('192.168.99.9')

loop = asyncio.get_event_loop()


def print_u(text):
    print('\033[4m' + text + '\033[0m')


print('Searching for NiKo Home Control Controllers and profiles on them...')
try:
    results = loop.run_until_complete(disc.get_all_profiles())
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()

print(results)
