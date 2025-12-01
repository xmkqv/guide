import 'dart:convert';

import 'package:flet/flet.dart';
import 'package:flutter/material.dart';
import 'package:vyuh_node_flow/vyuh_node_flow.dart';

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
  late NodeFlowController<String> _controller;
  final Map<String, Map<String, dynamic>> _nodeData = {};

  @override
  void initState() {
    super.initState();
    _controller = NodeFlowController<String>();
    _setupFlow();
  }

  @override
  void didUpdateWidget(SpecFlowControl oldWidget) {
    super.didUpdateWidget(oldWidget);
    _setupFlow();
  }

  void _setupFlow() {
    _controller.clear();
    _nodeData.clear();

    final nodesJson = widget.control.attrString("nodes", "[]")!;
    final connectionsJson = widget.control.attrString("connections", "[]")!;

    final List<dynamic> nodesData = jsonDecode(nodesJson);
    final List<dynamic> connectionsData = jsonDecode(connectionsJson);

    for (final nodeData in nodesData) {
      final id = nodeData['id'] as String;
      final label = nodeData['label'] as String? ?? id;
      final nodeType = nodeData['node_type'] as String? ?? 'child';
      final x = (nodeData['x'] as num?)?.toDouble() ?? 0.0;
      final y = (nodeData['y'] as num?)?.toDouble() ?? 0.0;

      _nodeData[id] = {
        'label': label,
        'node_type': nodeType,
      };

      final isRoot = nodeType == 'root';

      _controller.addNode(Node<String>(
        id: id,
        type: nodeType,
        position: Offset(x, y),
        data: label,
        inputPorts: isRoot ? const [] : const [Port(id: 'in', name: 'Input')],
        outputPorts: const [Port(id: 'out', name: 'Output')],
      ));
    }

    for (final connData in connectionsData) {
      final connId = connData['id'] as String;
      final sourceId = connData['source_id'] as String;
      final targetId = connData['target_id'] as String;

      _controller.addConnection(Connection(
        id: connId,
        sourceNodeId: sourceId,
        sourcePortId: 'out',
        targetNodeId: targetId,
        targetPortId: 'in',
      ));
    }
  }

  Widget _buildNode(BuildContext context, Node<String> node) {
    final data = _nodeData[node.id] ?? {'label': node.id, 'node_type': 'child'};
    final isRoot = data['node_type'] == 'root';
    final bgColor = isRoot ? Colors.blue.shade900 : Colors.grey.shade800;

    return GestureDetector(
      onTap: () => _handleNodeTap(node.id),
      child: Container(
        width: 140,
        padding: const EdgeInsets.all(12),
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
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.blue.shade700,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                node.id,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              data['label'] as String? ?? '',
              style: TextStyle(
                color: Colors.grey.shade300,
                fontSize: 10,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  void _handleNodeTap(String nodeId) {
    debugPrint("Node tapped: $nodeId");
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = NodeFlowTheme.dark.copyWith(
      backgroundColor: Colors.grey.shade900,
      connectionColor: Colors.blue.shade600,
      connectionWidth: 2.0,
    );

    Widget flowWidget = Container(
      color: Colors.grey.shade900,
      child: _controller.nodes.isEmpty
          ? Center(
              child: Text(
                'No specs defined',
                style: TextStyle(color: Colors.grey.shade500),
              ),
            )
          : NodeFlowViewer<String>(
              controller: _controller,
              theme: theme,
              nodeBuilder: _buildNode,
              enablePanning: true,
              enableZooming: true,
              scrollToZoom: true,
            ),
    );

    return constrainedControl(context, flowWidget, widget.parent, widget.control);
  }
}
