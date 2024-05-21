import { useEffect, useState } from 'react';
import './App.css';

function App() {
    const [forecasts, setForecasts] = useState();

    useEffect(() => {
        populateWeatherData();
    }, []);

    const contents = forecasts === undefined
        ? <p><em>Loading... Please refresh once the ASP.NET backend has started. See <a href="https://aka.ms/jspsintegrationreact">https://aka.ms/jspsintegrationreact</a> for more details.</em></p>
        : <table className="table table-striped" aria-labelledby="tabelLabel">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Temp. (C)</th>
                    <th>Temp. (F)</th>
                    <th>Summary</th>
                </tr>
            </thead>
            <tbody>
                {forecasts.map(forecast =>
                    <tr key={forecast.date}>
                        <td>{forecast.date}</td>
                        <td>{forecast.temperatureC}</td>
                        <td>{forecast.temperatureF}</td>
                        <td>{forecast.summary}</td>
                    </tr>
                )}
            </tbody>
        </table>;

    return (
        <div>
            <div class="container">
                <h1>Bem-vindo à Facial University</h1>
                <p>
                    Somos uma empresa dedicada à inovação e eficiência, oferecendo soluções
                    avançadas para o controle de presença e acesso em universidades.
                </p>

                <div class="topics">
                    <div>
                        <h2>
                            Exploramos métodos de controle de acesso, focando no desenvolvimento
                            de um dispositivo biométrico facial para controle de presença em
                            universidades.
                        </h2>
                        <div class="topic topic-1"></div>
                    </div>

                    <div class="in-topics">
                        <div>
                            <h2>Maior controle e segurança do ambiente</h2>
                            <div class="in-topic in-topic-1"></div>
                        </div>

                        <div>
                            <h2>Facilidade na chamada de presença</h2>
                            <div class="in-topic in-topic-2"></div>
                        </div>

                        <div>
                            <h2>Melhora na gestão de presença</h2>
                            <div class="in-topic in-topic-3"></div>
                        </div>
                    </div>

                    <div class="topic">
                        <h2>Plano de Valores</h2>
                        <p>
                            Oferecemos diferentes opções de planos para atender às necessidades
                            de sua universidade.
                        </p>
                        <div class="cost-plan">Plano de Teste: R$00,00/ 1° mês</div>
                        <div class="cost-plan">Plano Mensal: R$XX/mês</div>
                        <div class="cost-plan">Plano Anual: R$XXX/ano (economize XX%)</div>
                        <p>
                            Entre em contato conosco para personalizar um plano que atenda
                            melhor às suas necessidades e para discutir opções de pagamento e
                            financiamento.
                        </p>
                    </div>
                </div>
            </div>

            <footer>
                <div class="container">
                    <p>Facial University - Todos os direitos reservados</p>
                </div>
            </footer>

            <div class="contact-info">
                <div class="container center">
                    <p>
                        <a href="https://wa.me/11998877665" target="_blank">
                            <img
                                width="40"
                                height="40"
                                src="https://img.icons8.com/color/100/whatsapp--v1.png"
                                alt="whatsapp--v1"
                            />
                        </a>
                        <span>
                            Telefone Fixo:
                            <a href="https://wa.me/11998877665" target="_blank"
                            >35 3531-0000</a
                            ></span
                        >
                    </p>
                    <p>Endereço: Rua XXXXX, 0, Bairro XXXXX, Cidade XXXXX XXXXX XXX</p>
                </div>
            </div>
        </div>
    );
    
    async function populateWeatherData() {
        const response = await fetch('weatherforecast');
        const data = await response.json();
        setForecasts(data);
    }
}

export default App;