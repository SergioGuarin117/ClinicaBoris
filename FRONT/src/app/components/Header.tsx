import { Phone, Mail, Menu } from "lucide-react";
import { useState } from "react";

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setIsMenuOpen(false);
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 bg-white shadow-sm z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl text-blue-600">
              Dr. Boris Viafara
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <button
              onClick={() => scrollToSection("inicio")}
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Inicio
            </button>
            <button
              onClick={() => scrollToSection("sobre-mi")}
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Sobre Mí
            </button>
            <button
              onClick={() => scrollToSection("especialidades")}
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Especialidades
            </button>
            <button
              onClick={() => scrollToSection("separar-cita")}
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Separar Cita
            </button>
            <button
              onClick={() => scrollToSection("testimonios")}
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Testimonios
            </button>
            <button
              onClick={() => scrollToSection("contacto")}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Contacto
            </button>
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-gray-700"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="md:hidden pb-4 space-y-2">
            <button
              onClick={() => scrollToSection("inicio")}
              className="block w-full text-left py-2 text-gray-700 hover:text-blue-600"
            >
              Inicio
            </button>
            <button
              onClick={() => scrollToSection("sobre-mi")}
              className="block w-full text-left py-2 text-gray-700 hover:text-blue-600"
            >
              Sobre Mí
            </button>
            <button
              onClick={() => scrollToSection("especialidades")}
              className="block w-full text-left py-2 text-gray-700 hover:text-blue-600"
            >
              Especialidades
            </button>
            <button
              onClick={() => scrollToSection("separar-cita")}
              className="block w-full text-left py-2 text-gray-700 hover:text-blue-600"
            >
              Separar Cita
            </button>
            <button
              onClick={() => scrollToSection("testimonios")}
              className="block w-full text-left py-2 text-gray-700 hover:text-blue-600"
            >
              Testimonios
            </button>
            <button
              onClick={() => scrollToSection("contacto")}
              className="block w-full text-left py-2 text-blue-600"
            >
              Contacto
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}