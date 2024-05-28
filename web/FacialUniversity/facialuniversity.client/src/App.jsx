import React, { useState } from 'react';
import './App.css';
import RegistroEntradaSaida from './RegistroEntradaSaida';

function App() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [currentView, setCurrentView] = useState('inicio');

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const handleNavigation = (view) => {
        setCurrentView(view);
        setIsMenuOpen(false); 
    };

    return (
        <div>
            <nav>
                <button className="menu-toggle no-shadow" onClick={toggleMenu}>
                    ☰
                </button>
                <ul className={isMenuOpen ? 'open' : ''}>
                    <li><a href="#inicio" onClick={() => handleNavigation('inicio')}>INÍCIO</a></li>
                    <li className="has-submenu">
                        <a href="#acesso"  onClick={() => handleNavigation('acesso')}>ACESSO</a>
                        <ul>
                            <li className="has-submenu">
                                <a href="#relatorios" onClick={() => handleNavigation('relatorios')}>Relatórios</a>
                                <ul>
                                    <li><a href="#registro-entrada-saida" onClick={() => handleNavigation('registro-entrada-saida')}>Registro de Entrada e Saída</a></li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                    <li><a href="#planos" onClick={() => handleNavigation('planos')}>PLANOS</a></li>
                    <li><a href="#suporte" onClick={() => handleNavigation('suporte')}>SUPORTE</a></li>
                    <li><a href="#sobre" onClick={() => handleNavigation('sobre')}>SOBRE NÓS</a></li>
                </ul>
            </nav>
            <div className="container">
                {currentView === 'inicio' && (
                    <div id="inicio">
                        <h1>FACIAL UNIVERSITY</h1>
                        <p>
                            Somos uma empresa dedicada à inovação e eficiência, oferecendo soluções
                            avançadas para o controle de presença e acesso em universidades. Exploramos métodos de controle de acesso, focando no desenvolvimento
                            de um dispositivo biométrico facial para controle de presença em
                            universidades.
                        </p>
                        <div className="buttons">
                            <button className="btn">Solicitar Teste</button>
                            <button className="btn">Assinar</button>
                        </div>
                    </div>
                )}
                {currentView === 'registro-entrada-saida' && <RegistroEntradaSaida />}
            </div>
        </div>
    );
}

export default App;
