def print_answer(result: dict) -> None:
    print("\n" + "=" * 80)
    print("QUERY")
    print("=" * 80)
    print(result["query"])

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result["answer"] or "[DRY RUN – no answer generated]")

    print("\n" + "=" * 80)
    print("COST")
    print("=" * 80)

    cost = result["cost"]
    print(f"Input tokens:   {cost['input_tokens']}")
    print(f"Output tokens:  {cost['output_tokens']}")
    print(f"Total tokens:   {cost['total_tokens']}")
    print(f"Est. cost ($):  {cost['estimated_cost']:.6f}")

    print("=" * 80)
