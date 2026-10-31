import java.lang.reflect.Array;
import java.util.*;

/** Minimal JSON parser/serializer plus conversion between JSON values and the judge's type grammar. */
final class Json {
    private static final int MAX_NODES = 1_000_000;

    private final String s;
    private int pos;

    private Json(String s) { this.s = s; }

    static Object parse(String text) {
        Json p = new Json(text);
        p.ws();
        Object v = p.value();
        p.ws();
        if (p.pos != p.s.length()) throw new IllegalArgumentException("Trailing characters in JSON");
        return v;
    }

    private void ws() {
        while (pos < s.length() && Character.isWhitespace(s.charAt(pos))) pos++;
    }

    private Object value() {
        char c = s.charAt(pos);
        switch (c) {
            case '[': return array();
            case '{': return object();
            case '"': return string();
            case 't': pos += 4; return Boolean.TRUE;
            case 'f': pos += 5; return Boolean.FALSE;
            case 'n': pos += 4; return null;
            default: return number();
        }
    }

    private List<Object> array() {
        pos++;
        List<Object> list = new ArrayList<>();
        ws();
        if (s.charAt(pos) == ']') { pos++; return list; }
        while (true) {
            ws();
            list.add(value());
            ws();
            char c = s.charAt(pos++);
            if (c == ']') return list;
            if (c != ',') throw new IllegalArgumentException("Expected , or ] at " + pos);
        }
    }

    private Map<String, Object> object() {
        pos++;
        Map<String, Object> map = new LinkedHashMap<>();
        ws();
        if (s.charAt(pos) == '}') { pos++; return map; }
        while (true) {
            ws();
            String key = string();
            ws();
            pos++; // ':'
            ws();
            map.put(key, value());
            ws();
            char c = s.charAt(pos++);
            if (c == '}') return map;
            if (c != ',') throw new IllegalArgumentException("Expected , or } at " + pos);
        }
    }

    private String string() {
        pos++;
        StringBuilder sb = new StringBuilder();
        while (true) {
            char c = s.charAt(pos++);
            if (c == '"') return sb.toString();
            if (c == '\\') {
                char e = s.charAt(pos++);
                switch (e) {
                    case 'n': sb.append('\n'); break;
                    case 't': sb.append('\t'); break;
                    case 'r': sb.append('\r'); break;
                    case 'b': sb.append('\b'); break;
                    case 'f': sb.append('\f'); break;
                    case 'u': sb.append((char) Integer.parseInt(s.substring(pos, pos + 4), 16)); pos += 4; break;
                    default: sb.append(e);
                }
            } else {
                sb.append(c);
            }
        }
    }

    private Object number() {
        int start = pos;
        boolean isFloat = false;
        while (pos < s.length()) {
            char c = s.charAt(pos);
            if (c == '.' || c == 'e' || c == 'E') isFloat = true;
            else if (!(c == '-' || c == '+' || Character.isDigit(c))) break;
            pos++;
        }
        String num = s.substring(start, pos);
        return isFloat ? (Object) Double.parseDouble(num) : (Object) Long.parseLong(num);
    }

    // ---- serialization -------------------------------------------------

    static String stringify(Object v) {
        StringBuilder sb = new StringBuilder();
        write(sb, v);
        return sb.toString();
    }

    /** Like stringify, but knows the judge type, so a null ListNode/TreeNode is written as []. */
    static String stringify(Object v, String type) {
        StringBuilder sb = new StringBuilder();
        writeTyped(sb, v, type);
        return sb.toString();
    }

    private static void writeTyped(StringBuilder sb, Object v, String type) {
        if (v == null && (type.equals("ListNode") || type.equals("TreeNode"))) {
            sb.append("[]");
        } else if (v != null && type.contains("Node") && (type.endsWith("[]") || type.startsWith("list<"))) {
            String inner = type.endsWith("[]") ? type.substring(0, type.length() - 2) : type.substring(5, type.length() - 1);
            sb.append('[');
            if (v.getClass().isArray()) {
                for (int i = 0; i < Array.getLength(v); i++) {
                    if (i > 0) sb.append(',');
                    writeTyped(sb, Array.get(v, i), inner);
                }
            } else {
                boolean first = true;
                for (Object o : (Iterable<?>) v) {
                    if (!first) sb.append(',');
                    first = false;
                    writeTyped(sb, o, inner);
                }
            }
            sb.append(']');
        } else {
            write(sb, v);
        }
    }

    private static void writeList(StringBuilder sb, ListNode node) {
        sb.append('[');
        for (int n = 0; node != null; node = node.next, n++) {
            if (n >= MAX_NODES) throw new IllegalStateException("Returned linked list has a cycle (or more than 1,000,000 nodes)");
            if (n > 0) sb.append(',');
            sb.append(node.val);
        }
        sb.append(']');
    }

    private static void writeTree(StringBuilder sb, TreeNode root) {
        List<TreeNode> level = new ArrayList<>();
        level.add(root);
        List<String> out = new ArrayList<>();
        int count = 0;
        while (!level.isEmpty()) {
            List<TreeNode> next = new ArrayList<>();
            for (TreeNode node : level) {
                if (node == null) { out.add("null"); continue; }
                if (++count > MAX_NODES) throw new IllegalStateException("Returned tree has a cycle (or more than 1,000,000 nodes)");
                out.add(Integer.toString(node.val));
                next.add(node.left);
                next.add(node.right);
            }
            level = next;
        }
        int end = out.size();
        while (end > 0 && out.get(end - 1).equals("null")) end--;
        sb.append('[').append(String.join(",", out.subList(0, end))).append(']');
    }

    private static void write(StringBuilder sb, Object v) {
        if (v == null) {
            sb.append("null");
        } else if (v instanceof String || v instanceof Character) {
            quote(sb, v.toString());
        } else if (v instanceof Double || v instanceof Float) {
            double d = ((Number) v).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) sb.append("null");
            else sb.append(d);
        } else if (v instanceof Number || v instanceof Boolean) {
            sb.append(v);
        } else if (v instanceof ListNode) {
            writeList(sb, (ListNode) v);
        } else if (v instanceof TreeNode) {
            writeTree(sb, (TreeNode) v);
        } else if (v.getClass().isArray()) {
            sb.append('[');
            int n = Array.getLength(v);
            for (int i = 0; i < n; i++) {
                if (i > 0) sb.append(',');
                write(sb, Array.get(v, i));
            }
            sb.append(']');
        } else if (v instanceof Iterable) {
            sb.append('[');
            boolean first = true;
            for (Object o : (Iterable<?>) v) {
                if (!first) sb.append(',');
                first = false;
                write(sb, o);
            }
            sb.append(']');
        } else if (v instanceof Map) {
            sb.append('{');
            boolean first = true;
            for (Map.Entry<?, ?> e : ((Map<?, ?>) v).entrySet()) {
                if (!first) sb.append(',');
                first = false;
                quote(sb, String.valueOf(e.getKey()));
                sb.append(':');
                write(sb, e.getValue());
            }
            sb.append('}');
        } else {
            quote(sb, v.toString());
        }
    }

    private static void quote(StringBuilder sb, String str) {
        sb.append('"');
        for (int i = 0; i < str.length(); i++) {
            char c = str.charAt(i);
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
            }
        }
        sb.append('"');
    }

    // ---- type grammar --------------------------------------------------

    /** Java class for a judge type such as "int", "string[]", "list<list<int>>". */
    static Class<?> classFor(String type) {
        if (type.endsWith("[]")) {
            return Array.newInstance(classFor(type.substring(0, type.length() - 2)), 0).getClass();
        }
        if (type.startsWith("list<")) return List.class;
        switch (type) {
            case "int": return int.class;
            case "long": return long.class;
            case "double": return double.class;
            case "boolean": return boolean.class;
            case "char": return char.class;
            case "string": return String.class;
            case "void": return void.class;
            case "ListNode": return ListNode.class;
            case "TreeNode": return TreeNode.class;
        }
        throw new IllegalArgumentException("Unknown type " + type);
    }

    /** Convert a parsed JSON value into the Java value for the given judge type. */
    static Object convert(Object v, String type) {
        if (v == null) return null;
        if (type.endsWith("[]")) {
            String inner = type.substring(0, type.length() - 2);
            List<?> list = (List<?>) v;
            Object arr = Array.newInstance(classFor(inner), list.size());
            for (int i = 0; i < list.size(); i++) Array.set(arr, i, convert(list.get(i), inner));
            return arr;
        }
        if (type.startsWith("list<")) {
            String inner = type.substring(5, type.length() - 1);
            List<Object> out = new ArrayList<>();
            for (Object o : (List<?>) v) out.add(convert(o, inner));
            return out;
        }
        switch (type) {
            case "int": return ((Number) v).intValue();
            case "long": return ((Number) v).longValue();
            case "double": return ((Number) v).doubleValue();
            case "boolean": return (Boolean) v;
            case "char": return ((String) v).charAt(0);
            case "string": return (String) v;
            case "ListNode": {
                ListNode head = null;
                List<?> vals = (List<?>) v;
                for (int i = vals.size() - 1; i >= 0; i--) head = new ListNode(((Number) vals.get(i)).intValue(), head);
                return head;
            }
            case "TreeNode": return buildTree((List<?>) v);
        }
        throw new IllegalArgumentException("Unknown type " + type);
    }

    private static TreeNode buildTree(List<?> vals) {
        if (vals.isEmpty() || vals.get(0) == null) return null;
        TreeNode root = new TreeNode(((Number) vals.get(0)).intValue());
        List<TreeNode> level = new ArrayList<>(List.of(root));
        int i = 1;
        while (!level.isEmpty() && i < vals.size()) {
            List<TreeNode> next = new ArrayList<>();
            for (TreeNode node : level) {
                for (int side = 0; side < 2; side++, i++) {
                    if (i >= vals.size() || vals.get(i) == null) continue;
                    TreeNode child = new TreeNode(((Number) vals.get(i)).intValue());
                    if (side == 0) node.left = child; else node.right = child;
                    next.add(child);
                }
            }
            level = next;
        }
        return root;
    }
}
