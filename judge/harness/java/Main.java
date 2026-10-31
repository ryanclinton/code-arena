import java.io.*;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/**
 * Java test harness. Usage: java Main <job.json> <results.jsonl>
 * Loads the user's Solution class reflectively, so this file is compiled once and reused.
 */
public final class Main {
    private static final int MAX_STDOUT = 10_000;

    public static void main(String[] args) throws Exception {
        Thread t = new Thread(null, () -> {
            try {
                run(args[0], args[1]);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }, "judge", 512L * 1024 * 1024);
        t.start();
        t.join();
    }

    @SuppressWarnings("unchecked")
    private static void run(String jobPath, String resultsPath) throws Exception {
        Map<String, Object> job = (Map<String, Object>) Json.parse(Files.readString(Path.of(jobPath)));
        String methodName = (String) job.get("method");
        List<Object> paramTypes = (List<Object>) job.get("param_types");
        Object outputArgObj = job.get("output_arg");
        Integer outputArg = outputArgObj == null ? null : ((Number) outputArgObj).intValue();
        List<Object> tests = (List<Object>) job.get("tests");
        String resultType = outputArg != null ? (String) paramTypes.get(outputArg) : (String) job.get("return_type");

        PrintStream realOut = System.out;
        try (BufferedWriter out = Files.newBufferedWriter(Path.of(resultsPath), StandardCharsets.UTF_8)) {
            Class<?> cls;
            Method method;
            try {
                cls = Class.forName("Solution");
                Class<?>[] classes = new Class<?>[paramTypes.size()];
                for (int i = 0; i < classes.length; i++) classes[i] = Json.classFor((String) paramTypes.get(i));
                method = findMethod(cls, methodName, classes);
                method.setAccessible(true);
            } catch (Throwable e) {
                emit(out, "{\"fatal\":" + Json.stringify(e.toString()) + "}");
                return;
            }

            for (int i = 0; i < tests.size(); i++) {
                List<Object> raw = (List<Object>) tests.get(i);
                Object[] callArgs = new Object[raw.size()];
                for (int j = 0; j < callArgs.length; j++) callArgs[j] = Json.convert(raw.get(j), (String) paramTypes.get(j));

                ByteArrayOutputStream buf = new ByteArrayOutputStream();
                System.setOut(new PrintStream(buf, true, StandardCharsets.UTF_8));
                String line;
                try {
                    var ctor = cls.getDeclaredConstructor();
                    ctor.setAccessible(true);
                    Object instance = ctor.newInstance();
                    long start = System.nanoTime();
                    Object result = method.invoke(instance, callArgs);
                    long elapsed = System.nanoTime() - start;
                    Object output = outputArg != null ? callArgs[outputArg] : result;
                    line = "{\"i\":" + i + ",\"status\":\"ok\",\"output\":" + Json.stringify(output, resultType)
                            + ",\"time_ns\":" + elapsed + ",\"stdout\":" + Json.stringify(captured(buf)) + "}";
                } catch (InvocationTargetException e) {
                    line = errorLine(i, e.getCause(), buf);
                } catch (Throwable e) {
                    line = errorLine(i, e, buf);
                } finally {
                    System.setOut(realOut);
                }
                emit(out, line);
            }
        }
    }

    private static Method findMethod(Class<?> cls, String name, Class<?>[] params) throws NoSuchMethodException {
        try {
            return cls.getDeclaredMethod(name, params);
        } catch (NoSuchMethodException e) {
            StringBuilder sig = new StringBuilder();
            for (Class<?> c : params) sig.append(sig.length() > 0 ? ", " : "").append(c.getSimpleName());
            throw new NoSuchMethodException("Solution must define method " + name + "(" + sig + ")");
        }
    }

    private static String errorLine(int i, Throwable e, ByteArrayOutputStream buf) {
        String msg;
        if (e instanceof StackOverflowError) {
            msg = "java.lang.StackOverflowError";
        } else {
            StringWriter sw = new StringWriter();
            sw.append(e.toString()).append('\n');
            for (StackTraceElement el : e.getStackTrace()) {
                if (el.getClassName().startsWith("jdk.internal.reflect") || el.getClassName().equals("Main")
                        || el.getClassName().startsWith("java.lang.reflect")) break;
                if (el.getClassName().equals("Json")) continue;
                sw.append("  at ").append(el.toString()).append('\n');
            }
            msg = sw.toString();
        }
        return "{\"i\":" + i + ",\"status\":\"error\",\"error\":" + Json.stringify(msg)
                + ",\"stdout\":" + Json.stringify(captured(buf)) + "}";
    }

    private static String captured(ByteArrayOutputStream buf) {
        String s = buf.toString(StandardCharsets.UTF_8);
        return s.length() > MAX_STDOUT ? s.substring(0, MAX_STDOUT) : s;
    }

    private static void emit(BufferedWriter out, String line) throws IOException {
        out.write(line);
        out.write('\n');
        out.flush();
    }
}
