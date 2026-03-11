import React, { useState, ChangeEvent, FormEvent } from "react"; // ensure React types are available

const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CEDULA_REGEX = /^\d{6,10}$/;

type Field = {
  value: string;
  error: string;
  touched: boolean;
};

// Names of every form field; exported so helper components can reference
export type Fields = {
  nombre: Field;
  apellido: Field;
  cedula: Field;
  email: Field;
  telefono: Field;
  password: Field;
  confirmPassword: Field;
};

const emptyField = (): Field => ({ value: "", error: "", touched: false });

export default function RegisterPatient() {

  // we cast to Fields because the React typings are unavailable
  const [fields, setFields] = useState({
    nombre: emptyField(),
    apellido: emptyField(),
    cedula: emptyField(),
    email: emptyField(),
    telefono: emptyField(),
    password: emptyField(),
    confirmPassword: emptyField(),
  } as Fields);
  const [habeasData, setHabeasData] = useState(false);
  const [habeasError, setHabeasError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState("");

  const validate = (name: keyof Fields, value: string): string => {
    switch (name) {
      case "nombre":
      case "apellido":
        return value.trim().length < 2 ? "Debe tener al menos 2 caracteres." : "";
      case "cedula":
        return !CEDULA_REGEX.test(value) ? "La cédula debe tener entre 6 y 10 dígitos numéricos." : "";
      case "email":
        return !EMAIL_REGEX.test(value) ? "Ingresa un correo electrónico válido." : "";
      case "telefono":
        return value && !/^\d{7,15}$/.test(value) ? "Teléfono inválido (7-15 dígitos)." : "";
      case "password":
        return !PASSWORD_REGEX.test(value)
          ? "Mínimo 8 caracteres, mayúscula, minúscula, número y símbolo (@$!%*?&)."
          : "";
      case "confirmPassword":
        return value !== fields.password.value ? "Las contraseñas no coinciden." : "";
      default:
        return "";
    }
  };

  const handleChange = (name: keyof Fields, value: string) => {
    const error = validate(name, value);
    setFields((prev: Fields) => ({
      ...prev,
      [name]: { value, error, touched: true },
    }));
    // Re-validate confirmPassword when password changes
    if (name === "password") {
      const confErr =
        fields.confirmPassword.touched && value !== fields.confirmPassword.value
          ? "Las contraseñas no coinciden."
          : fields.confirmPassword.touched && value === fields.confirmPassword.value
          ? ""
          : fields.confirmPassword.error;
      setFields((prev: Fields) => ({
        ...prev,
        password: { value, error, touched: true },
        confirmPassword: { ...prev.confirmPassword, error: confErr },
      }));
    }
  };

  const handleBlur = (name: keyof Fields) => {
    const error = validate(name, fields[name].value);
    setFields((prev: Fields) => ({
      ...prev,
      [name]: { ...prev[name], error, touched: true },
    }));
  };

  const allValid = () => {
    const keys = Object.keys(fields) as Array<keyof Fields>;
    return (
      keys.every((k) => {
        if (k === "telefono") return true; // optional
        return fields[k].value.trim() !== "" && validate(k, fields[k].value) === "";
      }) && habeasData
    );
  };

  // use a loose type to avoid needing React's FormEvent
  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setHabeasError(!habeasData ? "Debes aceptar la política de tratamiento de datos." : "");

    // Touch all fields
    const touched: Fields = {} as Fields;
    (Object.keys(fields) as Array<keyof Fields>).forEach((k) => {
      touched[k] = { ...fields[k], error: validate(k, fields[k].value), touched: true };
    });
    setFields(touched);

    if (!allValid()) return;

    setLoading(true);
    setServerError("");

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre: fields.nombre.value,
          apellido: fields.apellido.value,
          cedula: fields.cedula.value,
          email: fields.email.value,
          telefono: fields.telefono.value,
          password: fields.password.value,
          rol: "paciente",
          habeas_data: habeasData,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        setServerError(data.detail || "Error al registrar. Intenta de nuevo.");
      } else {
        setSubmitted(true);
      }
    } catch {
      setServerError("No se pudo conectar al servidor. Verifica tu conexión.");
    } finally {
      setLoading(false);
    }
  };

  /* ─── SUCCESS SCREEN ─── */
  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f0f4f8]" style={{ fontFamily: "'Crimson Pro', Georgia, serif" }}>
        <style>{googleFonts}</style>
        <div className="bg-white rounded-3xl shadow-2xl p-12 max-w-md w-full text-center">
          <div className="w-20 h-20 bg-[#1a7a4a] rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" className="w-10 h-10">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-[#0d2b1d] mb-2">¡Registro exitoso!</h2>
          <p className="text-[#4a7060] text-lg mb-8">
            Tu cuenta de paciente ha sido creada. Ya puedes agendar y gestionar tus citas médicas.
          </p>
          <a
            href="/dashboard"
            className="inline-block bg-[#1a7a4a] text-white px-8 py-3 rounded-xl text-lg font-semibold hover:bg-[#155e38] transition-colors"
          >
            Ir al inicio
          </a>
        </div>
      </div>
    );
  }

  /* ─── FORM ─── */
  return (
    <div className="min-h-screen bg-[#f0f4f8] flex items-center justify-center px-4 py-12" style={{ fontFamily: "'Crimson Pro', Georgia, serif" }}>
      <style>{googleFonts + customCSS}</style>

      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 bg-[#1a7a4a]/10 text-[#1a7a4a] px-4 py-1.5 rounded-full text-sm font-semibold mb-4 tracking-wide uppercase">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <line x1="19" y1="8" x2="19" y2="14" />
              <line x1="22" y1="11" x2="16" y2="11" />
            </svg>
            Nuevo Paciente
          </div>
          <h1 className="text-4xl font-bold text-[#0d2b1d] mb-2">Crear tu cuenta</h1>
          <p className="text-[#4a7060] text-lg">Completa tus datos para agendar y gestionar tus citas</p>
        </div>

        {/* Card */}
        <form onSubmit={handleSubmit} noValidate className="bg-white rounded-3xl shadow-xl p-8 md:p-10">

          {/* Server error */}
          {serverError && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 rounded-xl px-5 py-4 text-sm flex gap-3">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 flex-shrink-0 mt-0.5">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {serverError}
            </div>
          )}

          {/* Row 1: Nombre / Apellido */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
            <InputField label="Nombre" name="nombre" field={fields.nombre} onChange={handleChange} onBlur={handleBlur} placeholder="Ej: María" />
            <InputField label="Apellido" name="apellido" field={fields.apellido} onChange={handleChange} onBlur={handleBlur} placeholder="Ej: García" />
          </div>

          {/* Row 2: Cédula / Teléfono */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
            <InputField
              label="Número de cédula"
              name="cedula"
              field={fields.cedula}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Ej: 1234567890"
              type="text"
              inputMode="numeric"
              maxLength={10}
              hint="6 a 10 dígitos"
            />
            <InputField
              label="Teléfono (opcional)"
              name="telefono"
              field={fields.telefono}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Ej: 3001234567"
              type="tel"
            />
          </div>

          {/* Email */}
          <div className="mb-5">
            <InputField
              label="Correo electrónico"
              name="email"
              field={fields.email}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="correo@ejemplo.com"
              type="email"
            />
          </div>

          {/* Passwords */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
            <PasswordField
              label="Contraseña"
              name="password"
              field={fields.password}
              show={showPassword}
              toggleShow={() => setShowPassword((v: boolean) => !v)}
              onChange={handleChange}
              onBlur={handleBlur}
              hint="≥8 chars, mayúscula, número, símbolo"
            />
            <PasswordField
              label="Confirmar contraseña"
              name="confirmPassword"
              field={fields.confirmPassword}
              show={showConfirm}
              toggleShow={() => setShowConfirm((v: boolean) => !v)}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </div>

          {/* Password strength */}
          {fields.password.value && (
            <PasswordStrength password={fields.password.value} />
          )}

          {/* Habeas Data */}
          <div className={`mt-6 rounded-2xl border-2 p-5 transition-colors ${habeasError ? "border-red-300 bg-red-50" : habeasData ? "border-[#1a7a4a] bg-[#f0faf4]" : "border-[#d1e5d9] bg-[#f8fbf9]"}`}>
            <label className="flex gap-3 cursor-pointer select-none">
              <div className="relative flex-shrink-0 mt-0.5">
                <input
                  type="checkbox"
                  checked={habeasData}
                  onChange={(e: any) => { setHabeasData(e.target.checked); setHabeasError(""); }}
                  className="sr-only"
                />
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${habeasData ? "bg-[#1a7a4a] border-[#1a7a4a]" : "bg-white border-gray-300"}`}>
                  {habeasData && (
                    <svg viewBox="0 0 12 12" fill="none" stroke="white" strokeWidth="2.5" className="w-3 h-3">
                      <polyline points="1 6 4 9 11 2" />
                    </svg>
                  )}
                </div>
              </div>
              <span className="text-sm text-[#2d5040] leading-relaxed">
                He leído y acepto la{" "}
                <a href="/politica-datos" target="_blank" className="text-[#1a7a4a] font-semibold underline underline-offset-2 hover:text-[#155e38]">
                  Política de Tratamiento de Datos Personales (Habeas Data)
                </a>{" "}
                y autorizo a ClinicaBoris el uso de mi información para la gestión de mis citas médicas.
              </span>
            </label>
            {habeasError && (
              <p className="text-red-600 text-xs mt-2 ml-8">{habeasError}</p>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="mt-8 w-full bg-[#1a7a4a] hover:bg-[#155e38] disabled:bg-[#7ab89a] text-white font-bold text-lg py-4 rounded-2xl transition-all shadow-lg hover:shadow-xl active:scale-[0.99] flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" strokeOpacity=".25" />
                  <path d="M12 2a10 10 0 0 1 10 10" />
                </svg>
                Registrando...
              </>
            ) : (
              <>
                Crear mi cuenta
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

/* ─── Sub-components ─── */

function InputField({
  label,
  name,
  field,
  onChange,
  onBlur,
  placeholder,
  type = "text",
  inputMode,
  maxLength,
  hint,
}: {
  label: string;
  name: keyof Fields;
  field: Field;
  onChange: (n: keyof Fields, v: string) => void;
  onBlur: (n: keyof Fields) => void;
  placeholder?: string;
  type?: string;
  inputMode?: string; // loosened because React types are not available
  maxLength?: number;
  hint?: string;
}) {
  const hasError = field.touched && field.error;
  const isOk = field.touched && !field.error && field.value;
  return (
    <div>
      <label className="block text-sm font-semibold text-[#0d2b1d] mb-1.5">{label}</label>
      <div className="relative">
        <input
          type={type}
          inputMode={inputMode}
          maxLength={maxLength}
          value={field.value}
          onChange={(e: any) => onChange(name, e.target.value)}
          onBlur={() => onBlur(name)}
          placeholder={placeholder}
          className={`w-full px-4 py-3 rounded-xl border-2 text-[#0d2b1d] placeholder-[#9eb8a8] bg-white transition-all outline-none text-base
            ${hasError ? "border-red-400 bg-red-50 focus:border-red-500" : isOk ? "border-[#1a7a4a] focus:border-[#1a7a4a]" : "border-[#d1e5d9] focus:border-[#1a7a4a]"}`}
        />
        {isOk && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[#1a7a4a]">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-4 h-4">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </span>
        )}
      </div>
      {hasError && <p className="text-red-500 text-xs mt-1">{field.error}</p>}
      {hint && !hasError && <p className="text-[#8aab97] text-xs mt-1">{hint}</p>}
    </div>
  );
}

function PasswordField({
  label,
  name,
  field,
  show,
  toggleShow,
  onChange,
  onBlur,
  hint,
}: {
  label: string;
  name: keyof Fields;
  field: Field;
  show: boolean;
  toggleShow: () => void;
  onChange: (n: keyof Fields, v: string) => void;
  onBlur: (n: keyof Fields) => void;
  hint?: string;
}) {
  const hasError = field.touched && field.error;
  const isOk = field.touched && !field.error && field.value;
  return (
    <div>
      <label className="block text-sm font-semibold text-[#0d2b1d] mb-1.5">{label}</label>
      <div className="relative">
        <input
          type={show ? "text" : "password"}
          value={field.value}
          onChange={(e: any) => onChange(name, e.target.value)}
          onBlur={() => onBlur(name)}
          placeholder="••••••••"
          className={`w-full px-4 py-3 pr-10 rounded-xl border-2 text-[#0d2b1d] placeholder-[#9eb8a8] bg-white transition-all outline-none text-base
            ${hasError ? "border-red-400 bg-red-50 focus:border-red-500" : isOk ? "border-[#1a7a4a] focus:border-[#1a7a4a]" : "border-[#d1e5d9] focus:border-[#1a7a4a]"}`}
        />
        <button type="button" onClick={toggleShow} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#4a7060] hover:text-[#1a7a4a]">
          {show ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
              <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          )}
        </button>
      </div>
      {hasError && <p className="text-red-500 text-xs mt-1">{field.error}</p>}
      {hint && !hasError && <p className="text-[#8aab97] text-xs mt-1">{hint}</p>}
    </div>
  );
}

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: "8+ caracteres", ok: password.length >= 8 },
    { label: "Mayúscula", ok: /[A-Z]/.test(password) },
    { label: "Minúscula", ok: /[a-z]/.test(password) },
    { label: "Número", ok: /\d/.test(password) },
    { label: "Símbolo", ok: /[@$!%*?&]/.test(password) },
  ];
  const score = checks.filter((c) => c.ok).length;
  const colors = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#1a7a4a"];
  const labels = ["Muy débil", "Débil", "Regular", "Buena", "Fuerte"];

  return (
    <div className="mb-5 p-4 bg-[#f8fbf9] rounded-xl border border-[#d1e5d9]">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-[#4a7060]">Fortaleza de contraseña</span>
        <span className="text-xs font-bold" style={{ color: colors[score - 1] || "#9ca3af" }}>{labels[score - 1] || "—"}</span>
      </div>
      <div className="flex gap-1 mb-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-1.5 flex-1 rounded-full transition-all" style={{ backgroundColor: i <= score ? colors[score - 1] : "#d1d5db" }} />
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {checks.map((c) => (
          <span key={c.label} className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.ok ? "bg-[#1a7a4a]/10 text-[#1a7a4a]" : "bg-gray-100 text-gray-400"}`}>
            {c.ok ? "✓" : "·"} {c.label}
          </span>
        ))}
      </div>
    </div>
  );
}

const googleFonts = `@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&display=swap');`;
const customCSS = `* { box-sizing: border-box; } body { margin: 0; }`;