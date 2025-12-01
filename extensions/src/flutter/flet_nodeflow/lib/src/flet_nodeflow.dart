import 'dart:convert';

import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:graphview/GraphView.dart';

class SpecFlowControl extends StatefulWidget {
  final Control? parent;
  final Control control;

  const SpecFlowControl({
    super.key,
    required this.parent,
    required this.control,
  });

  @override
  State<SpecFlowControl> createState() => _SpecFlowControlState();
}

class _SpecFlowControlState extends State<SpecFlowControl> {
  final Graph _graph = Graph()..isTree = true;
  final Map<String, Node> _nodes = {};
  final Map<String, Map<String, dynamic>> _nodeData = {};
  late BuchheimWalkerConfiguration _builder;
  late TransformationController _transformController;

  @override
  void initState() {
    super.initState();
    _transformController = TransformationController();
    _builder = BuchheimWalkerConfiguration()
      ..siblingSeparation = 40
      ..levelSeparation = 80
      ..subtreeSeparation = 60
      ..orientation = BuchheimWalkerConfiguration.ORIENTATION_TOP_BOTTOM;
    _setupGraph();
  }

  @override
  void didUpdateWidget(SpecFlowControl oldWidget) {
    super.didUpdateWidget(oldWidget);
    _setupGraph();
  }

  void _setupGraph() {
    _graph.nodes.clear();
    _graph.edges.clear();
    _nodes.clear();
    _nodeData.clear();

    final nodesJson = widget.control.attrString("nodes", "[]")!;
    final connectionsJson = widget.control.attrString("connections", "[]")!;

    final List<dynamic> nodesData = jsonDecode(nodesJson);
    final List<dynamic> connectionsData = jsonDecode(connectionsJson);

    // Create nodes
    for (final data in nodesData) {
      final id = data['id'] as String;
      final node = Node.Id(id);
      _nodes[id] = node;
      _nodeData[id] = {
        'label': data['label'] as String? ?? id,
        'node_type': data['node_type'] as String? ?? 'child',
      };
      _graph.addNode(node);
    }

    // Create edges
    for (final conn in connectionsData) {
      final sourceId = conn['source_id'] as String;
      final targetId = conn['target_id'] as String;
      final source = _nodes[sourceId];
      final target = _nodes[targetId];
      if (source != null && target != null) {
        _graph.addEdge(source, target);
      }
    }
  }

  Widget _buildNode(Node node) {
    final id = node.key?.value as String? ?? '';
    final data = _nodeData[id] ?? {'label': id, 'node_type': 'child'};
    final isRoot = data['node_type'] == 'root';
    final bgColor = isRoot ? Colors.blue.shade900 : Colors.grey.shade800;

    return Container(
      width: 120,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: bgColor,
        border: Border.all(color: Colors.grey.shade600),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(50),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: Colors.blue.shade700,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              id,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            data['label'] as String? ?? '',
            style: TextStyle(
              color: Colors.grey.shade300,
              fontSize: 9,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _transformController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Widget flowWidget;

    if (_graph.nodes.isEmpty) {
      flowWidget = Container(
        color: Colors.grey.shade900,
        child: Center(
          child: Text(
            'No specs defined',
            style: TextStyle(color: Colors.grey.shade500),
          ),
        ),
      );
    } else {
      flowWidget = Container(
        color: Colors.grey.shade900,
        child: InteractiveViewer(
          constrained: false,
          boundaryMargin: const EdgeInsets.all(200),
          minScale: 0.3,
          maxScale: 2.0,
          transformationController: _transformController,
          child: GraphView(
            graph: _graph,
            algorithm: BuchheimWalkerAlgorithm(
              _builder,
              TreeEdgeRenderer(_builder),
            ),
            paint: Paint()
              ..color = Colors.blue.shade600
              ..strokeWidth = 2
              ..style = PaintingStyle.stroke,
            builder: (Node node) => _buildNode(node),
          ),
        ),
      );
    }

    return constrainedControl(context, flowWidget, widget.parent, widget.control);
  }
}
