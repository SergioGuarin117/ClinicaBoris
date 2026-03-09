import { Hero } from "./components/Hero";
import { About } from "./components/About";
import { Specialties } from "./components/Specialties";
import { WhyChooseUs } from "./components/WhyChooseUs";
import { Testimonials } from "./components/Testimonials";
import { Contact } from "./components/Contact";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import { Appointment } from "./components/Appointment";

export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <Header />
      <Hero />
      <About />
      <Specialties />
      <WhyChooseUs />
      <Appointment />
      <Testimonials />
      <Contact />
      <Footer />
    </div>
  );
}