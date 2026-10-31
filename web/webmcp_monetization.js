// WebMCP Monetization Layer - Gumroad license-gated tool access.
// Uses Gumroad's public License Verification API directly from the
// browser. No payment-processor SDK or crypto library required.

const GUMROAD_PRODUCT_PERMALINK = "opvxi";

async function verifyGumroadLicense(licenseKey) {
  if (!licenseKey || typeof licenseKey !== "string") {
    return { valid: false, reason: "no_license_key_provided" };
  }
  try {
    const resp = await fetch("https://api.gumroad.com/v2/licenses/verify", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        product_permalink: GUMROAD_PRODUCT_PERMALINK,
        license_key: licenseKey,
      }),
    });
    const data = await resp.json();
    if (data.success && data.purchase && !data.purchase.refunded && !data.purchase.chargebacked) {
      return { valid: true, reason: "licensed" };
    }
    return { valid: false, reason: data.message || "license_invalid" };
  } catch (err) {
    return { valid: false, reason: "verification_error: " + String(err) };
  }
}

function paywallResponse(toolName) {
  return {
    error: "payment_required",
    tool: toolName,
    message: "This tool requires an active XRP Signal Service license.",
    purchase_url: "https://prostarelite.gumroad.com/l/opvxi",
    hint: "Pass your Gumroad license key as the 'license_key' parameter.",
  };
}

window.__webmcpMonetization = { verifyGumroadLicense, paywallResponse };
