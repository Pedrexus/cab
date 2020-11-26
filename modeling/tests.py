QUESTION = "What are the symptoms of COVID-19?"
CONTEXT = (
    "Coronavirus disease 2019 (COVID-19) is a contagious respiratory and vascular disease caused by severe acute respiratory syndrome "
    "coronavirus 2 (SARS-CoV-2). The first case was identified in Wuhan, China in December 2019, though evidence suggests that the virus may "
    "have already been actively spreading months earlier in places such as Italy.Common symptoms of COVID-19 include fever, cough, fatigue, "
    "breathing difficulties, and loss of smell and taste. Symptoms begin one to fourteen days after exposure to the virus. While most people "
    "have mild symptoms, some people develop acute respiratory distress syndrome (ARDS). ARDS can be precipitated by cytokine storms, "
    "multi-organ failure, septic shock, and blood clots. Longer-term damage to organs (in particular, the lungs and heart) has been observed. "
    "There is concern about a significant number of patients who have recovered from the acute phase of the disease but continue to "
    "experience a range of effects—known as long COVID—for months afterwards. These effects include severe fatigue, memory loss and other "
    "cognitive issues, low grade fever, muscle weakness, and breathlessness "
)

if __name__ == '__main__':
    from src.model import CABModel

    model = CABModel(run_name="SQUAD")

    model.finetune(
        "data/QAdataset.txt",
        steps=1000,
        model_name='124M',
        model_dir='models',
        combine=50000,
        batch_size=1,
        learning_rate=0.0001,
        accumulate_gradients=5,
        restore_from='latest',
        sample_every=2000,
        sample_length=1023,
        sample_num=1,
        multi_gpu=False,
        save_every=100,
        print_every=1,
        max_checkpoints=1,
        use_memory_saving_gradients=False,
        only_train_transformer_layers=False,
        optimizer='adam',
        overwrite=False,
    )
