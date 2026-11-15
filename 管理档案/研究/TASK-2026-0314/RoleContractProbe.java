import java.text.AttributedCharacterIterator;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

class RoleContractProbe {
    record Case(String id, String pattern, String rendered, List<Integer> roles) {}
    public static void main(String[] args) {
        var data = new Object[]{"SENDER_TOKEN", "RECIPIENT_TOKEN"};
        var cases = List.of(
            new Case("baseline", "发送：{0}；接收：{1}", "发送：SENDER_TOKEN；接收：RECIPIENT_TOKEN", List.of(0, 1)),
            new Case("legal-reorder", "接收：{1}；发送：{0}", "接收：RECIPIENT_TOKEN；发送：SENDER_TOKEN", List.of(1, 0)),
            new Case("roles-inverted", "接收：{0}；发送：{1}", "接收：SENDER_TOKEN；发送：RECIPIENT_TOKEN", List.of(0, 1)),
            new Case("quoted-slot", "发送：'{0}'；接收：{1}", "发送：{0}；接收：RECIPIENT_TOKEN", List.of(1)),
            new Case("missing-index", "发送：{2}；接收：{1}", "发送：{2}；接收：RECIPIENT_TOKEN", List.of(1)),
            new Case("literal-mimic", "发送：SENDER_TOKEN；接收：{1}", "发送：SENDER_TOKEN；接收：RECIPIENT_TOKEN", List.of(1))
        );
        for (var c : cases) {
            var f = new MessageFormat(c.pattern(), Locale.SIMPLIFIED_CHINESE);
            AttributedCharacterIterator it = f.formatToCharacterIterator(data);
            var ordered = new ArrayList<Integer>();
            for (int i = it.getBeginIndex(); i < it.getEndIndex();) {
                it.setIndex(i);
                var index = it.getAttribute(MessageFormat.Field.ARGUMENT);
                if (index instanceof Integer n) ordered.add(n);
                i = it.getRunLimit(MessageFormat.Field.ARGUMENT);
            }
            String formatted = f.format(data);
            if (!formatted.equals(c.rendered()) || !ordered.equals(c.roles())) {
                throw new AssertionError(c.id() + " actual: " + formatted + " " + ordered);
            }
            String formatSlots = Arrays.toString(f.getFormatsByArgumentIndex());
            if (!c.id().equals("missing-index") && !formatSlots.equals("[null, null]")) {
                throw new AssertionError(c.id() + " format slots: " + formatSlots);
            }
            System.out.printf("%s | arguments=%s | subformats=%s | %s%n",
                              c.id(), ordered, formatSlots, formatted);
        }
    }
}
