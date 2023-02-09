import youtokentome as yttm
data = 'utils/manifests/atcc_all.json'# string, path to file with training data
model = 'test_tokenizer' # string, path to where the trained model will be saved
vocab_size = 400 # int, number of tokens in the final vocabulary
yttm.BPE.train(data, model, vocab_size)