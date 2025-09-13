from otter.test_files import test_case

OK_FORMAT = False

name = "p6"
points = 50

@test_case(points=10, hidden=False)
def test_heappush(heappush, env):
    """Run heappush and see if the results make sense"""
    assert_node2index_consistency = env['assert_node2index_consistency']
    check_heap_property = env['check_heap_property']
    heapprint = env['heapprint']
    heap = []
    node2index = {}
    for i in range(11, -1, -1):
        heappush(heap, node2index, i + 1)
        assert_node2index_consistency(heap, node2index)
        assert check_heap_property(heap, 0, len(heap) - 1)
    heapprint(heap)

@test_case(points=10, hidden=False)
def test_heappop(heappop, env):
    """Run heappop and see if the results make sense"""
    assert_node2index_consistency = env['assert_node2index_consistency']
    check_heap_property = env['check_heap_property']
    create_random_heap = env['create_random_heap']
    (heap, node2index) = create_random_heap()
    for _ in range(len(heap)):
        heappop(heap, node2index)
        assert_node2index_consistency(heap, node2index)
        assert check_heap_property(heap, 0, len(heap) - 1)

@test_case(points=10, hidden=False)
def test_heapreplace(heapreplace, env):
    """Run heapreplace and see if the results make sense"""
    assert_node2index_consistency = env['assert_node2index_consistency']
    check_heap_property = env['check_heap_property']
    create_random_heap = env['create_random_heap']
    heapprint = env['heapprint']
    import random
    (heap, node2index) = create_random_heap()
    heapprint(heap)
    old_item = heap[random.randint(0, len(heap) - 1)]
    new_item = 99
    print('Replacing %d with %d' % (old_item, new_item))
    heapreplace(heap, node2index, old_item, new_item)
    assert_node2index_consistency(heap, node2index)
    assert check_heap_property(heap, 0, len(heap) - 1)
    heapprint(heap)

@test_case(points=20, hidden=False)
def test_dijkstra(dijkstra, env):
    graph = env['graph']
    (success, search_path, node2parent, node2dist) = dijkstra(graph, 's', None, debug=True)
    print(success, node2parent, node2dist)
    assert node2dist['v'] == 9
    assert node2parent['v'] == 'u'
    assert node2parent == {'s': None, 'x': 's', 'u': 'x', 'v': 'u', 'y': 'x'}
    assert node2dist == {'s': 0, 'x': 5, 'u': 8, 'v': 9, 'y': 7}

