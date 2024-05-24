import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
    const [forecasts, setForecasts] = useState();

    useEffect(() => {
        populateWeatherData();
    }, []);

    return (
        <div>
            <nav>
                <ul>
                    <li><a href="#inicio">INÍCIO</a></li>
                    <li><a href="#acesso">ACESSO</a></li>
                    <li><a href="#planos">PLANOS</a></li>
                    <li><a href="#suporte">SUPORTE</a></li>
                    <li><a href="#sobre">SOBRE NÓS</a></li>
                </ul>
            </nav>
            <div className="container" id="inicio">
                <h1>FACIAL UNIVERSITY</h1>
                <p>
                    Somos uma empresa dedicada à inovação e eficiência, oferecendo soluções
                    avançadas para o controle de presença e acesso em universidades. Exploramos métodos de controle de acesso, focando no desenvolvimento
                    de um dispositivo biométrico facial para controle de presença em
                    universidades.
                </p>
                <div className="buttons-container">
                    <button className="btn">Solicitar Teste</button>
                    <button className="btn">Assinar</button>
                </div>
            </div>
        </div>
    );

    async function populateWeatherData() {
        try {
            const response = await fetch('weatherforecast');
            const data = await response.json();
            setForecasts(data);
        } catch (error) {
            console.error('Error fetching weather data:', error);
        }
    }
}

export default App;
