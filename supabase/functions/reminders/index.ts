// Sverige i fokus – påminnelsemejl till elever som inte övat på ett tag.
// POST (med x-cron-token)       -> skickar påminnelser (body: { dry_run?: bool, test_to?: string })
// GET  ?unsubscribe=<token>     -> avregistrerar eleven och visar en bekräftelsesida
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const APP_URL = "https://sverige-i-fokus-quiz.netlify.app";
const FN_URL = `${SUPABASE_URL}/functions/v1/reminders`;
const FROM = "Sverige i fokus – Admas Studio <info@admasstudio.se>";
const LOGO = "https://images.squarespace-cdn.com/content/v1/6a593dd1abd41a63f34e8097/80f85dff-ce16-4464-8b57-c9b41c200472/Logo_changed_name-removebg-preview.png?format=200w";

const db = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } });

type Candidate = {
  user_id: string; email: string; first_name: string | null; unsubscribe_token: string;
  passed: number; total: number; next_chapter_no: number | null; next_chapter_title: string | null;
  days_inactive: number; reminder_no: number;
};

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));

function buildEmail(c: Candidate) {
  const fn = c.first_name ? c.first_name.charAt(0).toLocaleUpperCase("sv") + c.first_name.slice(1) : "";
  const name = fn ? `, ${fn}` : "";
  const unsub = `${FN_URL}?unsubscribe=${c.unsubscribe_token}`;
  const pct = c.total ? Math.round((c.passed / c.total) * 100) : 0;
  const next = c.next_chapter_no ? `kapitel ${c.next_chapter_no} – ${c.next_chapter_title}` : "nästa kapitel";
  const subject = c.passed === 0
    ? `Kom igång med Sverige i fokus${name} – kapitel ${c.next_chapter_no ?? 1} väntar`
    : `Du har klarat ${c.passed} av ${c.total} kapitel${name} – fortsätt så!`;
  const intro = c.passed === 0
    ? `Du har tillgång till Sverige i fokus, men har inte klarat något kapitel ännu. Börja med några frågor i dag – det tar bara några minuter.`
    : `Det var ${c.days_inactive} dagar sedan du övade senast. Du har redan klarat <b>${c.passed} av ${c.total}</b> kapitel – bra jobbat! Några frågor om dagen gör stor skillnad inför medborgarskapsprovet.`;

  const html = `<!doctype html><html lang="sv"><body style="margin:0;background:#0a1628;font-family:Arial,Helvetica,sans-serif;color:#f7f4ed;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0a1628;padding:24px 12px;"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#152a4a;border-radius:6px;overflow:hidden;">
<tr><td style="height:6px;background:#f8ac00;"></td></tr>
<tr><td style="padding:26px 28px 6px;"><img src="${LOGO}" width="56" height="56" alt="Admas Studio" style="display:block;"></td></tr>
<tr><td style="padding:6px 28px 0;">
  <p style="margin:0 0 6px;font-size:12px;letter-spacing:2px;color:#f8ac00;font-weight:bold;">SVERIGE I FOKUS · MEDBORGARSKAPSPROV</p>
  <h1 style="margin:0 0 14px;font-size:26px;line-height:1.2;color:#f7f4ed;">Hej${esc(name)}! 👋</h1>
  <p style="margin:0 0 18px;font-size:16px;line-height:1.6;color:#c7d2e3;">${intro}</p>
</td></tr>
<tr><td style="padding:0 28px 6px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0f1f38;border-radius:4px;">
  <tr><td style="padding:14px 16px 6px;font-size:14px;color:#f7f4ed;font-weight:bold;">Dina framsteg: ${c.passed} av ${c.total} kapitel klara</td></tr>
  <tr><td style="padding:0 16px 14px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#1e3a5f;border-radius:4px;"><tr>
    <td width="${Math.max(pct, 2)}%" style="height:8px;background:#f06a28;border-radius:4px;font-size:0;line-height:0;">&nbsp;</td><td style="font-size:0;line-height:0;">&nbsp;</td></tr></table></td></tr>
  </table>
</td></tr>
<tr><td style="padding:18px 28px 6px;">
  <p style="margin:0 0 14px;font-size:15px;color:#f7f4ed;">Nästa steg: <b>${esc(next)}</b></p>
  <a href="${APP_URL}" style="display:inline-block;background:#f8ac00;color:#0a1628;text-decoration:none;font-weight:bold;font-size:16px;padding:14px 24px;border-radius:4px;">Fortsätt öva →</a>
  <p style="margin:16px 0 0;font-size:14px;line-height:1.6;color:#c7d2e3;">Tips: läs kapitlet på tigrinja eller lätt svenska först – sedan går frågorna lättare.</p>
</td></tr>
<tr><td style="padding:22px 28px 26px;font-size:12px;line-height:1.6;color:#8b9ab3;border-top:1px solid #1e3a5f;">
  Admas Studio · Styvingevägen 14C, 591 55 Motala · <a href="https://www.admasstudio.se" style="color:#8b9ab3;">admasstudio.se</a><br>
  Du får det här mejlet eftersom du har ett konto på Sverige i fokus. Frågor? Svara bara på mejlet.<br>
  <a href="${unsub}" style="color:#8b9ab3;">Avsluta påminnelser</a>
</td></tr>
</table></td></tr></table></body></html>`;

  const text = `Hej${name}!\n\n${intro.replace(/<[^>]+>/g, "")}\n\nDina framsteg: ${c.passed} av ${c.total} kapitel klara.\nNästa steg: ${next}\n\nFortsätt öva: ${APP_URL}\n\n—\nAdmas Studio · admasstudio.se\nAvsluta påminnelser: ${unsub}\n`;
  return { subject, html, text, unsub };
}

async function sendEmail(to: string, c: Candidate) {
  const { subject, html, text, unsub } = buildEmail(c);
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: FROM, to: [to], reply_to: "info@admasstudio.se", subject, html, text,
      headers: { "List-Unsubscribe": `<${unsub}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" },
    }),
  });
  if (!res.ok) throw new Error(`Resend ${res.status}: ${await res.text()}`);
  return await res.json();
}

function page(title: string, body: string) {
  return new Response(`<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title></head>
<body style="margin:0;background:#0a1628;color:#f7f4ed;font-family:Arial,sans-serif;display:flex;min-height:100vh;align-items:center;justify-content:center;padding:20px;">
<div style="max-width:440px;background:#152a4a;border-top:6px solid #f8ac00;border-radius:6px;padding:28px;text-align:center;">
<img src="${LOGO}" width="64" height="64" alt="Admas Studio"><h1 style="font-size:22px;">${title}</h1><p style="color:#c7d2e3;line-height:1.6;">${body}</p>
<a href="${APP_URL}" style="display:inline-block;margin-top:10px;background:#f8ac00;color:#0a1628;text-decoration:none;font-weight:bold;padding:12px 20px;border-radius:4px;">Till Sverige i fokus</a></div></body></html>`,
    { headers: { "Content-Type": "text/html; charset=utf-8" } });
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

Deno.serve(async (req) => {
  const url = new URL(req.url);

  // --- Avregistrering (GET från länken, eller POST one-click från mejlprogrammet) ---
  const token = url.searchParams.get("unsubscribe");
  if (token) {
    const ok = /^[0-9a-f-]{36}$/i.test(token)
      ? (await db.rpc("unsubscribe_reminders", { p_token: token })).data === true : false;
    if (req.method === "POST") return new Response(ok ? "ok" : "not found", { status: ok ? 200 : 404 });
    return ok
      ? page("Du får inga fler påminnelser", "Vi har stängt av påminnelsemejlen för ditt konto. Ditt konto och dina framsteg finns kvar – välkommen tillbaka när du vill!")
      : page("Länken fungerar inte", "Länken är ogiltig eller har redan använts. Kontakta info@admasstudio.se om du fortfarande får mejl.");
  }

  // --- Utskick (kräver intern token) ---
  if (req.method !== "POST") return new Response("Not found", { status: 404 });
  const { data: secret } = await db.from("app_secrets").select("value").eq("name", "cron_token").single();
  if (!secret || req.headers.get("x-cron-token") !== secret.value) return new Response("Forbidden", { status: 403 });
  if (!RESEND_API_KEY) return new Response("RESEND_API_KEY saknas", { status: 500 });

  const body = await req.json().catch(() => ({}));
  const { data: candidates, error } = await db.rpc("reminder_candidates");
  if (error) return new Response(error.message, { status: 500 });
  const list = (candidates ?? []) as Candidate[];

  if (body.dry_run) {
    return Response.json({ would_send: list.length, preview: list.slice(0, 3).map((c) => ({ ...buildEmail(c), html: undefined, to: c.email.replace(/^(.).*(@.*)$/, "$1***$2") })) });
  }
  if (body.test_to) {
    const sample: Candidate = list[0] ?? { user_id: "", email: "", first_name: "Dejen", unsubscribe_token: "00000000-0000-0000-0000-000000000000", passed: 5, total: 13, next_chapter_no: 6, next_chapter_title: "Exempelkapitel", days_inactive: 9, reminder_no: 1 };
    const r = await sendEmail(String(body.test_to), { ...sample, first_name: "Dejen", unsubscribe_token: "00000000-0000-0000-0000-000000000000" });
    return Response.json({ test_sent: true, id: r.id });
  }

  const max = Math.min(Number(body.limit) || 90, 90); // gratisnivån hos Resend: 100 mejl/dag
  let sent = 0; const failed: string[] = [];
  for (const c of list.slice(0, max)) {
    try {
      await sendEmail(c.email, c);
      await db.rpc("mark_reminded", { p_user_id: c.user_id, p_reminder_no: c.reminder_no });
      sent++;
    } catch (e) { failed.push(String(e).slice(0, 200)); }
    await sleep(600); // håll oss under Resends gräns (2 mejl/sekund)
  }
  return Response.json({ candidates: list.length, sent, failed: failed.length, errors: failed.slice(0, 3) });
});
