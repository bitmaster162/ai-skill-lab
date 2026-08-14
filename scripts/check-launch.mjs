const required = [
  "NEXT_PUBLIC_SITE_URL",
  "NEXT_PUBLIC_TELEGRAM_URL",
  "NEXT_PUBLIC_LEGAL_OPERATOR_NAME",
  "NEXT_PUBLIC_LEGAL_CONTACT_EMAIL",
  "NEXT_PUBLIC_LEGAL_JURISDICTION",
  "LEAD_WEBHOOK_URL",
  "LEAD_WEBHOOK_SECRET",
];

const errors = [];
for (const key of required) {
  if (!process.env[key]?.trim()) errors.push(`${key} is missing`);
}

for (const key of ["NEXT_PUBLIC_SITE_URL", "NEXT_PUBLIC_TELEGRAM_URL", "LEAD_WEBHOOK_URL"]) {
  const value = process.env[key];
  if (!value) continue;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:") errors.push(`${key} must use https`);
  } catch {
    errors.push(`${key} is not a valid URL`);
  }
}

if (process.env.NEXT_PUBLIC_SITE_URL?.includes("example.com")) errors.push("NEXT_PUBLIC_SITE_URL still uses example.com");
if (process.env.LEAD_WEBHOOK_SECRET && process.env.LEAD_WEBHOOK_SECRET.length < 24) errors.push("LEAD_WEBHOOK_SECRET must be at least 24 characters");
if (process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL)) errors.push("NEXT_PUBLIC_LEGAL_CONTACT_EMAIL is invalid");

if (errors.length) {
  console.error("LAUNCH_CHECK_FAIL");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log("LAUNCH_CHECK_PASS");
