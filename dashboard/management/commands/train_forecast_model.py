from django.core.management.base import BaseCommand

from forecasting.services import train_model


class Command(BaseCommand):
    help = 'Trains and compares Linear Regression vs Random Forest on Sales History, saves the best model.'

    def handle(self, *args, **options):
        result = train_model()
        if not result['success']:
            self.stdout.write(self.style.ERROR(result['reason']))
            return

        self.stdout.write(self.style.SUCCESS(f"Best model: {result['best_model']}"))
        for name, m in result['metrics'].items():
            self.stdout.write(f"  {name}: MAE={m['mae']:.2f}  RMSE={m['rmse']:.2f}  R2={m['r2']:.3f}")
        self.stdout.write(f"Training rows: {result['training_rows']}, Test rows: {result['test_rows']}")
        self.stdout.write(self.style.SUCCESS(f"Model saved to {result['model_path']}"))
