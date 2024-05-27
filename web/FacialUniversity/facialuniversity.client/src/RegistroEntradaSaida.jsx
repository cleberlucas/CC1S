import React, { useState, useEffect } from 'react';

const LoadingIndicator = () => {
    return (
        <div className="loading-container">
            <div className="loading-spinner"></div>
            <span>Carregando...</span>
        </div>
    );
};

const RegistroEntradaSaida = () => {
    const [dados, setDados] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/capture');
                const data = await response.json();
                const dadosComNomes = await Promise.all(data.map(async registro => {
                    if (registro.user_id === 0) {
                        return { ...registro, user_name: 'Desconhecido' };
                    } else {
                        const userResponse = await fetch(`http://127.0.0.1:5000/domains/university/user/user_id/${registro.user_id}`);
                        const userData = await userResponse.json();
                        return { ...registro, user_name: userData.name };
                    }
                }));
                setDados(dadosComNomes);
                setIsLoading(false);
            } catch (error) {
                console.error('Erro ao buscar dados:', error);
            }
        };

        const intervalId = setInterval(fetchData, 1000);

        return () => clearInterval(intervalId);
    }, []);

    const formatarDataHora = (dataHora) => {
        const data = new Date(dataHora);
        data.setHours(data.getHours() + 3);
        const dia = data.getDate().toString().padStart(2, '0');
        const mes = (data.getMonth() + 1).toString().padStart(2, '0');
        const ano = data.getFullYear();
        const horas = data.getHours().toString().padStart(2, '0');
        const minutos = data.getMinutes().toString().padStart(2, '0');
        const segundos = data.getSeconds().toString().padStart(2, '0');
        return `${dia}/${mes}/${ano} ${horas}:${minutos}:${segundos}`;
    };

    return (
        <div className="table-container" id="registro-entrada-saida">
            <h2>Registros de Entrada e Saída</h2>
            {isLoading ? (
                <LoadingIndicator />
            ) : (
                <div className="table-container-sub">
                    <table>
                        <thead>
                            <tr>
                                <th>&nbsp;ID&nbsp;</th>
                                <th>&nbsp;Nome&nbsp;</th>
                                <th>&nbsp;Ação&nbsp;</th>
                                <th>&nbsp;Horário&nbsp;</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dados.map(registro => (
                                <tr key={registro.id}>
                                    <td>&nbsp;{registro.id}</td>
                                    <td>&nbsp;{registro.user_name}</td>
                                    <td>&nbsp;{registro.door === 'entrance' ? 'Entrada' : 'Saída'}</td>
                                    <td>&nbsp;{formatarDataHora(registro.capture_time)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default RegistroEntradaSaida;
