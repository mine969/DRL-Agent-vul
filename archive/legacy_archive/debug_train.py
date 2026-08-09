import sys

sys.path.insert(0, "d:\\github\\DRL Agents\\DQN web vul")

try:
    from train_mock_targets import MockTargetsTrainer

    trainer = MockTargetsTrainer()
    print("✅ Trainer initialized successfully!")
    trainer.train(total_episodes=2)
except Exception as e:
    import traceback

    print("❌ ERROR:")
    print(traceback.format_exc())
