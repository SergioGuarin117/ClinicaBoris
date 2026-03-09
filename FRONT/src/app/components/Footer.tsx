import {
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
} from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-xl mb-4">Dr. Boris Viafara</h3>
            <p className="text-gray-400">
              Cirugía de alta especialidad con más de 15 años de
              experiencia al servicio de tu salud.
            </p>
          </div>

          <div>
            <h4 className="text-lg mb-4">Enlaces Rápidos</h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="#inicio"
                  className="text-gray-400 hover:text-white transition"
                >
                  Inicio
                </a>
              </li>
              <li>
                <a
                  href="#sobre-mi"
                  className="text-gray-400 hover:text-white transition"
                >
                  Sobre Mí
                </a>
              </li>
              <li>
                <a
                  href="#especialidades"
                  className="text-gray-400 hover:text-white transition"
                >
                  Especialidades
                </a>
              </li>
              <li>
                <a
                  href="#contacto"
                  className="text-gray-400 hover:text-white transition"
                >
                  Contacto
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-lg mb-4">Especialidades</h4>
            <ul className="space-y-2 text-gray-400">
              <li>Cirugía Laparoscópica</li>
              <li>Cirugía General</li>
              <li>Cirugía Bariátrica</li>
              <li>Cirugía de Tiroides</li>
            </ul>
          </div>

          <div>
            <h4 className="text-lg mb-4">Síguenos</h4>
            <div className="flex gap-4">
              <a
                href="#"
                className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition"
              >
                <Instagram className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="#"
                className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
          <p>
            &copy; 2026 Dr. Boris Viafara. Todos los derechos
            reservados.
          </p>
          <p className="mt-2 text-sm">
            Cédula Profesional: 1234567 | Cédula de
            Especialidad: 7654321
          </p>
        </div>
      </div>
    </footer>
  );
}