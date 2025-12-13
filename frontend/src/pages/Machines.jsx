import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Machines() {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState({});
  const [selectedMachine, setSelectedMachine] = useState(null);

  const API_BASE = "/api/machines"; // FastAPI router prefix

  useEffect(() => {
    fetchMachines();
  }, []);

  const fetchMachines = async () => {
    setLoading(true);
    try {
      const res = await axios.get(API_BASE);
      setMachines(res.data);
    } catch (err) {
      console.error(err);
      alert("Erreur lors du chargement des machines");
    } finally {
      setLoading(false);
    }
  };

  const toggleBlock = async (machine) => {
    try {
      const endpoint =
        machine.status === "blocked" ? "unblock" : "block";
      await axios.post(`${API_BASE}/${machine.id}/${endpoint}`, {
        reason: "Action admin",
      });
      fetchMachines();
      if (selectedMachine) fetchLogs(selectedMachine.id);
    } catch (err) {
      console.error(err);
      alert("Impossible de changer le statut");
    }
  };

  const fetchLogs = async (machineId) => {
    try {
      const res = await axios.get(`${API_BASE}/${machineId}/logs`);
      setLogs((prev) => ({ ...prev, [machineId]: res.data }));
      setSelectedMachine(machines.find((m) => m.id === machineId));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Machines / Pharmagest</h1>
      {loading ? (
        <p>Chargement...</p>
      ) : (
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2">ID</th>
              <th className="border p-2">Nom</th>
              <th className="border p-2">MAC</th>
              <th className="border p-2">Owner</th>
              <th className="border p-2">Statut</th>
              <th className="border p-2">Dernière connexion</th>
              <th className="border p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {machines.map((m) => (
              <tr key={m.id}>
                <td className="border p-2">{m.id}</td>
                <td className="border p-2">{m.device_name}</td>
                <td className="border p-2">{m.mac_address}</td>
                <td className="border p-2">{m.owner || "-"}</td>
                <td className="border p-2">
                  <span
                    className={
                      m.status === "blocked"
                        ? "text-red-600 font-bold"
                        : "text-green-600 font-bold"
                    }
                  >
                    {m.status.toUpperCase()}
                  </span>
                </td>
                <td className="border p-2">
                  {m.last_seen ? new Date(m.last_seen).toLocaleString() : "-"}
                </td>
                <td className="border p-2">
                  <button
                    className={`px-3 py-1 rounded ${
                      m.status === "blocked"
                        ? "bg-green-500 text-white"
                        : "bg-red-500 text-white"
                    }`}
                    onClick={() => toggleBlock(m)}
                  >
                    {m.status === "blocked" ? "Débloquer" : "Bloquer"}
                  </button>
                  <button
                    className="ml-2 px-3 py-1 bg-blue-500 text-white rounded"
                    onClick={() => fetchLogs(m.id)}
                  >
                    Logs
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Logs */}
      {selectedMachine && logs[selectedMachine.id] && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="text-xl font-bold mb-2">
            Logs pour {selectedMachine.device_name}
          </h2>
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2">Action</th>
                <th className="border p-2">Par</th>
                <th className="border p-2">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {logs[selectedMachine.id].map((log, idx) => (
                <tr key={idx}>
                  <td className="border p-2">{log.action}</td>
                  <td className="border p-2">{log.by_user}</td>
                  <td className="border p-2">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
