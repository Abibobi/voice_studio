import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Navbar() {
  const { isLoggedIn, user, logout } = useAuth();
  const nav = useNavigate();

  const handleLogout = () => {
    logout();
    nav("/");
  };

  return (
    <nav className="nav" id="main-nav">
      <Link to="/" className="nav__logo">
        🎙️ Voice Studio
      </Link>

      <div className="nav__links">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `nav__link ${isActive ? "nav__link--active" : ""}`
          }
        >
          Home
        </NavLink>

        {isLoggedIn ? (
          <>
            <NavLink
              to="/models"
              className={({ isActive }) =>
                `nav__link ${isActive ? "nav__link--active" : ""}`
              }
            >
              Models
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `nav__link ${isActive ? "nav__link--active" : ""}`
              }
            >
              Dashboard
            </NavLink>

            <div className="nav__user">
              <span className="nav__avatar">
                {user?.email?.charAt(0).toUpperCase()}
              </span>
              <button className="nav__link nav__logout-btn" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <NavLink
              to="/login"
              className={({ isActive }) =>
                `nav__link ${isActive ? "nav__link--active" : ""}`
              }
            >
              Sign In
            </NavLink>
            <NavLink
              to="/signup"
              className={({ isActive }) =>
                `btn btn--sm ${isActive ? "" : ""}`
              }
            >
              Get Started
            </NavLink>
          </>
        )}
      </div>
    </nav>
  );
}
