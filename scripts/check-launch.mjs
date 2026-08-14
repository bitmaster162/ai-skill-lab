const formEnabled = process.env.NEXT_PUBLIC_LEAD_FORM_ENABLED === "true";
const errors = [];
const warnings = [];

const requiredAlways = ["NEXT_PUBLIC_SITE_URL", "NEXT_PUBLIC_TELEGRAM_URL"];
for (const key of requiredAlways) {
  if (!process.env[key]?.trim()) errors.push(`${key} is missing`);
}

for (const key of ["NEXT_PUBLIC_SITE_URL", "NEXT_PUBLIC_TELEGRAM_URL"]) {
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

if (formEnabled) {
  const requiredForForm = [
    "NEXT_PUBLIC_LEGAL_OPERATOR_NAME",
    "NEXT_PUBLIC_LEGAL_CONTACT_EMAIL",
    "NEXT_PUBLIC_LEGAL_JURISDICTION",
    "LEAD_WEBHOOK_URL",
    "LEAD_WEBHOOK_SECRET",
  ];
  for (const key of requiredForForm) {
    if (!process.env[key]?.trim()) errors.push(`${key} is missing while lead form is enabled`);
  }

  if (process.env.LEAD_WEBHOOK_URL) {
    try {
      const url = new URL(process.env.LEAD_WEBHOOK_URL);
      if (url.protocol !== "https:") errors.push("LEAD_WEBHOOK_URL must use https");
    } catch {
      errors.push("LEAD_WEBHOOK_URL is not a valid URL");
    }
  }
  if (process.env.LEAD_WEBHOOK_SECRET && process.env.LEAD_WEBHOOK_SECRET.length < 24) errors.push("LEAD_WEBHOOK_SECRET must be at least 24 characters");
  if (process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL)) errors.push("NEXT_PUBLIC_LEGAL_CONTACT_EMAIL is invalid");
} else {
  warnings.push("lead form disabled: launch is contact-only via public messenger links");
  if (!process.env.NEXT_PUBLIC_LEGAL_OPERATOR_NAME?.trim()) warnings.push("legal operator not configured yet");
  if (!process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL?.trim()) warnings.push("legal contact email not configured yet");
}

if (errors.length) {
  console.error("LAUNCH_CHECK_FAIL");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log("LAUNCH_CHECK_PASS");
for (const warning of warnings) console.warn(`- WARNING: ${warning}`);
