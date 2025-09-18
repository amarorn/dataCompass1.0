// Script de inicialização do MongoDB para DataCompass 1.0

// Conectar ao banco datacompass
db = db.getSiblingDB('datacompass');

// Criar usuário da aplicação
db.createUser({
  user: 'datacompass_user',
  pwd: 'datacompass_app_2025',
  roles: [
    {
      role: 'readWrite',
      db: 'datacompass'
    }
  ]
});

// Criar coleções principais
db.createCollection('users');
db.createCollection('interactions');
db.createCollection('clients');
db.createCollection('insights');
db.createCollection('processed_csvs');
db.createCollection('message_history');

// Criar índices para performance
db.users.createIndex({ "whatsappNumber": 1 }, { unique: true });
db.interactions.createIndex({ "userId": 1, "timestamp": -1 });
db.clients.createIndex({ "userId": 1 });
db.processed_csvs.createIndex({ "from": 1, "processedAt": -1 });
db.message_history.createIndex({ "from": 1, "timestamp": -1 });
db.message_history.createIndex({ "type": 1, "timestamp": -1 });

// Inserir dados de exemplo
db.users.insertOne({
  _id: ObjectId(),
  whatsappNumber: "558498671188",
  name: "Usuário Demo",
  registeredAt: new Date(),
  isActive: true
});

print("✅ Banco de dados DataCompass inicializado com sucesso!");
print("📊 Coleções criadas: users, interactions, clients, insights, processed_csvs, message_history");
print("🔐 Usuário da aplicação: datacompass_user");
print("📈 Índices criados para otimização");
