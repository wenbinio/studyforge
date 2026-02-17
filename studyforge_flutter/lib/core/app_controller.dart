import 'database_service.dart';
import 'config_service.dart';
import 'ai_service.dart';
import 'models.dart';
import 'srs_service.dart';

class AppController {
  AppController({
    required this.database,
    required this.configService,
    required this.ai,
    required this.srs,
  });

  final DatabaseService database;
  final ConfigService configService;
  final AiService ai;
  final SrsService srs;

  AppConfig _config = const AppConfig();

  AppConfig get config => _config;

  Future<void> initialize() async {
    _config = await configService.loadConfig();
    await database.database;
  }

  Future<void> saveConfig(AppConfig config) async {
    await configService.saveConfig(config);
    _config = config;
  }
}
