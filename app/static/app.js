function buildRequest() {
  const req = {
    origin: document.getElementById("origin").value.trim(),
    destination: document.getElementById("destination").value.trim(),
    depart_after: document.getElementById("depart_after").value.trim(),
    arrive_before: document.getElementById("arrive_before").value.trim(),
    max_layovers: Number(document.getElementById("max_layovers").value),
    optimize_for: document.getElementById("optimize_for").value,
  };

  return req;
}

function setStatus(msg) {
  document.getElementById("status").textContent = msg || "";
}

function renderResults(data) {
  const el = document.getElementById("results");
  el.innerHTML = "";

  const plans = data?.plans || [];
  if (!Array.isArray(plans) || plans.length === 0) {
    el.innerHTML = `<div class="muted">No plans returned.</div>`;
    return;
  }

  for (const p of plans) {
    const score = p.score ?? "—";
    const price = p.metrics?.total_price_gbp ?? "—";
    const duration = p.metrics?.total_duration_minutes ?? "—";
    const emissions = p.metrics?.total_emissions_kg ?? "—";
    const risk = p.metrics?.risk_score ?? "—";
    const legs = p.legs ?? [];

    const card = document.createElement("div");
    card.className = "result";

    const legsHtml = Array.isArray(legs)
      ? legs.map(l => {
          const from = l.origin ?? "?";
          const to = l.destination ?? "?";
          const provider = l.provider ?? "provider";
          const mins = l.duration_minutes ?? "";
          const mode = l.mode ?? "";
          return `<li><b>${from}</b> → <b>${to}</b> <span class="muted">(${provider}, ${mode}${mins ? `, ${mins}m` : ""})</span></li>`;
        }).join("")
      : "";

    const expl = p.explanation ?? "";

    card.innerHTML = `
      <div class="top">
        <div><b>Score:</b> ${score}</div>
        <div><b>Price:</b> £${price}</div>
        <div><b>Duration:</b> ${duration}m</div>
        <div><b>Emissions:</b> ${emissions} kg</div>
        <div><b>Risk:</b> ${risk}</div>
      </div>
      <div class="body">
        <ul>${legsHtml}</ul>
        ${expl ? `<details><summary>Explanation</summary><pre>${escapeHtml(expl)}</pre></details>` : ""}
        <button class="book-btn" onclick="bookPlan(${escapeHtml(JSON.stringify(p))})">Book This Plan</button>
      </div>
    `;

    el.appendChild(card);
  }
}

// Booking flow functions
async function bookPlan(plan) {
  setStatus("Creating booking...");

  try {
    const resp = await fetch("/api/bookings", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ plan }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      setStatus(`Booking failed: ${data?.detail || "unknown error"}`);
      return;
    }

    setStatus(`Booking created: ${data.id}`);
    showBookingDetails(data);
  } catch (e) {
    setStatus(`Booking request failed: ${e?.message || e}`);
  }
}

function showBookingDetails(booking) {
  const modal = document.createElement("div");
  modal.className = "modal";
  modal.innerHTML = `
    <div class="modal-content">
      <h3>Booking Created</h3>
      <p><b>Booking ID:</b> ${escapeHtml(booking.id)}</p>
      <p><b>Status:</b> ${escapeHtml(booking.status)}</p>
      <p><b>Price:</b> £${booking.total_price_gbp}</p>
      <p><b>Hold expires:</b> ${new Date(booking.hold_expires_at).toLocaleString()}</p>

      <h4>Passenger Information</h4>
      <input type="text" id="passenger_name" placeholder="Full Name" required>
      <input type="email" id="passenger_email" placeholder="Email" required>
      <input type="text" id="passenger_passport" placeholder="Passport Number (optional)">

      <div class="modal-actions">
        <button onclick="confirmBooking('${booking.id}')">Confirm & Pay</button>
        <button onclick="closeModal()">Cancel</button>
        <button onclick="viewBooking('${booking.id}')">View Details</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

async function confirmBooking(bookingId) {
  const name = document.getElementById("passenger_name").value;
  const email = document.getElementById("passenger_email").value;
  const passport = document.getElementById("passenger_passport").value;

  if (!name || !email) {
    alert("Please provide name and email");
    return;
  }

  setStatus("Confirming booking...");

  try {
    const resp = await fetch(`/api/bookings/${bookingId}/confirm`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        passenger_data: {
          full_name: name,
          email: email,
          passport_number: passport || null,
        }
      }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      setStatus(`Confirmation failed: ${data?.detail || "unknown error"}`);
      return;
    }

    setStatus(`Booking confirmed! Payment ref: ${data.payment_reference}`);
    closeModal();
    showSuccessMessage(data);
  } catch (e) {
    setStatus(`Confirmation request failed: ${e?.message || e}`);
  }
}

async function viewBooking(bookingId) {
  setStatus("Loading booking details...");

  try {
    const resp = await fetch(`/api/bookings/${bookingId}`);
    const data = await resp.json();

    if (!resp.ok) {
      setStatus(`Failed to load booking: ${data?.detail || "unknown error"}`);
      return;
    }

    displayBookingDetails(data);
  } catch (e) {
    setStatus(`Request failed: ${e?.message || e}`);
  }
}

function displayBookingDetails(booking) {
  closeModal();

  const modal = document.createElement("div");
  modal.className = "modal";

  const auditHtml = booking.audit_trail?.map(log =>
    `<li><b>${log.action}</b> at ${new Date(log.timestamp).toLocaleString()}</li>`
  ).join("") || "";

  modal.innerHTML = `
    <div class="modal-content">
      <h3>Booking Details</h3>
      <p><b>ID:</b> ${escapeHtml(booking.id)}</p>
      <p><b>Status:</b> ${escapeHtml(booking.status)}</p>
      <p><b>Price:</b> £${booking.total_price_gbp}</p>
      ${booking.payment_reference ? `<p><b>Payment Ref:</b> ${escapeHtml(booking.payment_reference)}</p>` : ""}

      ${booking.passenger_data ? `
        <h4>Passenger</h4>
        <p><b>Name:</b> ${escapeHtml(booking.passenger_data.full_name)}</p>
        <p><b>Email:</b> ${escapeHtml(booking.passenger_data.email)}</p>
      ` : ""}

      <h4>Audit Trail</h4>
      <ul class="audit-trail">${auditHtml}</ul>

      <div class="modal-actions">
        <button onclick="closeModal()">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

function showSuccessMessage(booking) {
  const modal = document.createElement("div");
  modal.className = "modal";
  modal.innerHTML = `
    <div class="modal-content success">
      <h3>✓ Booking Confirmed!</h3>
      <p><b>Booking ID:</b> ${escapeHtml(booking.id)}</p>
      <p><b>Payment Reference:</b> ${escapeHtml(booking.payment_reference)}</p>
      <p><b>Total Paid:</b> £${booking.total_price_gbp}</p>
      <p>Confirmation email sent to ${escapeHtml(booking.passenger_data?.email || "")}</p>
      <div class="modal-actions">
        <button onclick="closeModal()">Done</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

function closeModal() {
  const modals = document.querySelectorAll(".modal");
  modals.forEach(m => m.remove());
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function runSearch() {
  const req = buildRequest();
  document.getElementById("requestPreview").textContent = JSON.stringify(req, null, 2);

  setStatus("Searching…");
  document.getElementById("results").innerHTML = "";

  try {
    // If your endpoint differs, change this one line:
    const resp = await fetch("/api/search", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(req),
    });

    const text = await resp.text();
    const data = text ? JSON.parse(text) : {};

    if (!resp.ok) {
      setStatus(`Error ${resp.status}: ${data?.detail || text || "unknown"}`);
      return;
    }

    setStatus(`OK (${resp.status})`);
    renderResults(data);
  } catch (e) {
    setStatus(`Request failed: ${e?.message || e}`);
  }
}

document.getElementById("searchBtn").addEventListener("click", runSearch);

// live preview of request JSON
["origin","destination","depart_after","arrive_before","max_layovers","optimize_for"].forEach(id => {
  const el = document.getElementById(id);
  el.addEventListener("input", () => {
    const req = buildRequest();
    document.getElementById("requestPreview").textContent = JSON.stringify(req, null, 2);
  });
});
document.getElementById("requestPreview").textContent = JSON.stringify(buildRequest(), null, 2);