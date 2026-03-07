import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const { pathname } = useLocation();

  const links = [
    { to: "/upload",  label: "📤 Upload" },
    { to: "/gallery", label: "🖼️ Gallery" },
    { to: "/people",  label: "👤 People" },
    { to: "/chat",    label: "🤖 Chatbot" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="brand-icon">👁️</span>
        <span className="brand-name">Drishyamitra</span>
      </div>
      <div className="navbar-links">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`nav-link ${
              pathname === link.to || (link.to === "/upload" && pathname === "/")
                ? "active"
                : ""
            }`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
